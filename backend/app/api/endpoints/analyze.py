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

        # Retrieve relevant policy documents using RAG
        logger.info(f"Retrieving policies for platform: {platform}")
        policy_context = rag_service.query(platform, "What are the core community guidelines and safety policies?")
        
        # Construct Prompt with RAG Context
        prompt = f"""
        You are a content compliance expert for {platform}.
        Analyze this video for policy violations based on the following specific policy context:

        --- RELEVANT POLICY CONTEXT ---
        {policy_context}
        --- END OF CONTEXT ---
        
        CRITICAL INSTRUCTION: You MUST analyze both the AUDIO (transcript) and the VISUALS (frames).
        Look specifically for:
        - Weapons (guns, knives)
        - Drugs or paraphernalia
        - Violence or physical altercations
        - Text on screen that violates policy
        
        Output the result in strict JSON format with this structure:
        {{
            "platform": "{platform}",
            "risk_level": "Low" | "Medium" | "High",
            "summary_rationale": "A brief 2-sentence summary of why this risk level was assigned.",
            "issues": [
                {{
                    "category": "Category Name (e.g. Violence, Hate Speech, Dangerous Goods)",
                    "timestamp": "MM:SS (e.g. 01:23) or 'Entire Video'",
                    "snippet": "Visual description of the event OR text transcript",
                    "rationale": "Why this violates policy",
                    "policy_citations": ["Policy Name/Section"]
                }}
            ]
        }}
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
        
        result_dict = json.loads(cleaned_text.strip())
        
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
