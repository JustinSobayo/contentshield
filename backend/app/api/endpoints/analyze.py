from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from app.models.schemas import AnalyzeResponse, AnalyzeRequest
from app.services.gemini_service import analyze_multimodal
from app.services.redis_service import redis_service
from app.services.rag_service import rag_service
from app.core.security import limiter
import hashlib
import tempfile
import os
import json
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/minute")
async def analyze_content(
    request: Request,
    file: UploadFile = File(...),
    platform: str = Form(...)
):
    """
    Analyzes video content for policy violations using Gemini 1.5 Flash.
    """
    try:
        # Create a temp file for the video and generate hash without loading full file into memory
        suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
        sha256_hash = hashlib.sha256()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while chunk := await file.read(8192):
                sha256_hash.update(chunk)
                tmp.write(chunk)
            tmp_path = tmp.name

        file_hash = sha256_hash.hexdigest()
        cache_key = f"analyze:{platform}:{file_hash}"
        
        # Check cache
        cached_result = redis_service.get_cached_analysis(cache_key)
        if cached_result:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return AnalyzeResponse(**cached_result)

        # Retrieve relevant policy documents using RAG (run in thread to avoid event loop conflict)
        logger.info(f"Retrieving policies for platform: {platform}")
        policy_context = await asyncio.to_thread(
            rag_service.query, platform, "What are the core community guidelines and safety policies?"
        )
        
        # Construct Prompt with RAG Context
        prompt = f"""
        You are a STRICT content moderation AI for {platform}. Your job is to protect the platform from policy violations.
        You must be BRUTALLY HONEST and ERR ON THE SIDE OF CAUTION. If something MIGHT violate policy, flag it.
        
        Platforms are extremely strict about content moderation. A video that seems "borderline" to a human will likely be taken down.

        --- PLATFORM POLICY CONTEXT ---
        {policy_context}
        --- END OF CONTEXT ---
        
        CRITICAL INSTRUCTIONS:
        1. Analyze EVERY FRAME of the video carefully
        2. Analyze ALL AUDIO including speech, music, and background sounds
        3. Read ALL TEXT that appears on screen
        4. Consider the OVERALL TONE and MESSAGE of the content
        5. Be SKEPTICAL - assume the worst interpretation that a content moderator might take
        
        FLAG ANY OF THE FOLLOWING (this is NOT exhaustive - flag anything questionable):
        
        VIOLENCE & DANGEROUS CONTENT:
        - Weapons of ANY kind (guns, knives, bats, etc.) even if decorative or in background
        - Fighting, hitting, slapping, pushing - even if "playful" or staged
        - Dangerous stunts or challenges that could cause injury
        - Animal abuse or cruelty
        - Self-harm references or glorification
        
        DRUGS & CONTROLLED SUBSTANCES:
        - Any drug use, paraphernalia, or references (including marijuana in most regions)
        - Alcohol if shown irresponsibly or to minors
        - Prescription drug misuse
        - Smoking or vaping
        
        HATE & HARASSMENT:
        - Slurs or derogatory language (even if "reclaimed" or in music)
        - Mocking or targeting individuals or groups
        - Discriminatory content based on race, gender, religion, sexuality, disability
        - Bullying or intimidation
        
        SEXUAL & SUGGESTIVE CONTENT:
        - Nudity or partial nudity
        - Sexually suggestive poses, movements, or clothing
        - Sexual innuendo or explicit language
        - Content sexualizing minors in ANY way
        
        MISINFORMATION & DECEPTION:
        - Health misinformation
        - Political misinformation
        - Scams or misleading claims
        - Fake news or manipulated media
        
        OTHER VIOLATIONS:
        - Copyright music playing (popular songs without license)
        - Spam or misleading metadata
        - Promotion of illegal activities
        - Privacy violations (showing others without consent)
        - Graphic or disturbing imagery
        
        RISK LEVEL GUIDELINES (FOLLOW THESE STRICTLY):
        
        - HIGH: Use this if ANY of these are present:
          * Sexual content, nudity, or sexually suggestive material
          * Violence, weapons, or dangerous activities
          * Hate speech, slurs, or discriminatory content
          * Drug use or promotion
          * Content that could cause real-world harm
          * Multiple MEDIUM-level issues combined
        
        - MEDIUM: Use this if ANY of these are present:
          * Suggestive language or innuendo (like in this video with sexual slang)
          * Mild profanity or crude humor
          * Borderline content that MIGHT be flagged
          * Copyright concerns (popular music, etc.)
          * Any single policy concern that doesn't rise to HIGH
        
        - LOW: ONLY use this if the video is completely clean with NO issues found.
          * If you list ANY issues in the "issues" array, the risk level CANNOT be "Low"
        
        CRITICAL RULE: If you find issues worth mentioning, the risk level MUST be at least "Medium".
        A "Low" risk rating with issues listed is a CONTRADICTION - never do this.
        
        Output the result as a SINGLE JSON object (NOT an array). Use this exact structure:
        {{
            "platform": "{platform}",
            "risk_level": "Low" | "Medium" | "High",
            "summary_rationale": "A brief 2-sentence summary of why this risk level was assigned. Be specific about what was found.",
            "issues": [
                {{
                    "category": "Category Name",
                    "timestamp": "MM:SS or 'Entire Video'",
                    "snippet": "Specific description of what was seen/heard",
                    "rationale": "Why this violates or may violate {platform} policy"
                }}
            ]
        }}
        
        If NO issues are found, still explain why in summary_rationale and return an empty issues array.
        """

        # Call Gemini Service
        json_response_text = analyze_multimodal(prompt, file_path=tmp_path)
        
        # Clean up temp file
        os.remove(tmp_path)

        # Parse JSON
        # Clean potential markdown backticks
        cleaned_text = json_response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        result_data = json.loads(cleaned_text.strip())
        
        # Handle case where Gemini returns a list instead of a dict
        if isinstance(result_data, list):
            logger.warning(f"Gemini returned a list with {len(result_data)} items, extracting first element")
            if len(result_data) > 0:
                result_dict = result_data[0]
            else:
                raise ValueError("Gemini returned an empty list")
        else:
            result_dict = result_data
        
        logger.info(f"Parsed response keys: {result_dict.keys() if isinstance(result_dict, dict) else type(result_dict)}")
        
        # Validate with Pydantic
        response_model = AnalyzeResponse(**result_dict)
        
        # Cache the result (as dict)
        redis_service.set_cached_analysis(cache_key, result_dict)
        
        return response_model

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Clean up temp file component in case of error
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
