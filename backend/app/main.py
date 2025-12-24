from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import tempfile
import whisper
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# LlamaIndex imports
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import google.generativeai as genai

#For limiting API requests
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Load environment variables
# Construct absolute path to backend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR) # parent of app is backend
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

# Create the FastAPI app instance
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        os.getenv("FRONTEND_ORIGIN", "").strip() or "",
    ],
    allow_origin_regex=r"^https?://(localhost|127\\.0\\.0\\.1):\\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure LlamaIndex with Gemini
# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY not found in environment variables!")

genai.configure(api_key=api_key)
Settings.llm = Gemini(model="models/gemini-flash-latest", api_key=api_key)
Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004", api_key=api_key)

# Global variables for models and index
whisper_model = None
policy_index = None
chroma_client = None

# Pydantic models
class AnalyzeRequest(BaseModel):
    transcript: str
    platform: str

class AnalyzeResponse(BaseModel):
    platform: str
    risk_level: str
    issues: List[Dict[str, Any]]

# Health check endpoint
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Ensure Whisper model is initialized
def _ensure_whisper():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("base")
    return whisper_model

# Ensure Gemini is configured
def _ensure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not found")
    return genai.GenerativeModel("gemini-2.5-flash")

# Document processing and indexing
def _ensure_policy_index():
    global policy_index, chroma_client
    
    if policy_index is None:
        try:
            # Initialize Chroma client
            chroma_path = os.path.join(BACKEND_DIR, "chroma_db")
            chroma_client = chromadb.PersistentClient(path=chroma_path)#chroma client is initialized as a chromadb object so that i can make it a perstistant client such that data is stored on the disk so data survives server restarts
            chroma_collection = chroma_client.get_or_create_collection("policies")#collections used so that i can be able to have different types of data stored inside of the database as containers. for example, one container would be the user transcripts and another container would be the policy documents.
            
            # Create vector store
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Load documents if policy_docs folder exists
            policy_docs_path = os.path.join(BACKEND_DIR, "policy_docs")
            if os.path.exists(policy_docs_path):
                documents = SimpleDirectoryReader(policy_docs_path).load_data()
                if documents:
                    policy_index = VectorStoreIndex.from_documents(
                        documents, 
                        storage_context=storage_context,
                        show_progress=True
                    )
                else:
                    # Create empty index if no documents
                    policy_index = VectorStoreIndex.from_documents(
                        [], 
                        storage_context=storage_context
                    )
        except Exception as e:
            print(f"Warning: Could not load policy documents: {e}")
            # Create a simple in-memory index as fallback
            policy_index = VectorStoreIndex.from_documents([])
    
    return policy_index

# Test gemini connection
@app.get("/test-gemini")
def test_gemini_connection():
    try:
        model = _ensure_gemini()
        response = model.generate_content("Say 'API connection successful' and nothing else.")
        return {
            "status": "success",
            "message": response.text,
            "model_used": "gemini-2.0-flash-exp"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/transcribe")
@limiter.limit("5/minute")
def transcribe_video(request: Request, file: UploadFile = File(...)):
    logger.info(f"Transcribing file: {file.filename}")
    print(f"DEBUG: Transcribing file: {file.filename}")
    _ensure_whisper()
    
    try:
        if not file.content_type or not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Only video files are allowed")
        suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = file.file.read()
            tmp.write(content)
            path = tmp.name
        
        result = whisper_model.transcribe(path, fp16=False)
        text = result.get("text", "").strip()
        language = result.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text transcribed")
        
        return {"text": text, "language": language}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        try:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

# Analyze content with RAG pipeline
@app.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/minute")
def analyze_content(request: Request, req: AnalyzeRequest):
    logger.info(f"Analyzing content for platform: {req.platform}")    
    # Initialize variables to track progress
    policy_index = None
    query_engine = None
    policy_content = ""
    
    # --- STEP 1: Vector DB & Indexing ---
    try:
        policy_index = _ensure_policy_index()
        query_engine = policy_index.as_query_engine()
    except Exception as e:
        logger.error(f"Vector DB Error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "platform": req.platform,
            "risk_level": "Unknown",
            "issues": [{
                "category": "System Error",
                "snippet": "Vector Database Initialization Failed",
                "rationale": f"Could not access policy database. Reason: {str(e)}",
                "policy_citations": []
            }]
        }

    # --- STEP 2: RAG Retrieval ---
    try:
        policy_query = f"""
            What are the {req.platform} policies regarding prohibited content, community guidelines violations, and reasons for video takedowns?
            Include rules on safety, integrity, and sensitive topics.
            """
        policy_response = query_engine.query(policy_query)
        policy_content = str(policy_response)
        print(f"DEBUG: Policy content: {policy_content}")
    except Exception as e:
        logger.error(f"RAG Retrieval Error: {str(e)}")
        logger.error(traceback.format_exc())
        # can optionally continue without policy context, or fail here. 
        # fail to be explicit about the error.
        return {
            "platform": req.platform,
            "risk_level": "Unknown",
            "issues": [{
                "category": "System Error",
                "snippet": "Policy Retrieval Failed",
                "rationale": f"Could not retrieve relevant policies. Reason: {str(e)}",
                "policy_citations": []
            }]
        }

    # --- STEP 3: LLM Analysis ---
    try:
        analysis_prompt = f"""
            You are analyzing a video transcript for policy violations on {req.platform}.
            
            POLICY CONTEXT (retrieved from policy documents):
            {policy_content}
            
            VIDEO TRANSCRIPT:
            {req.transcript}
            
            TASK: Determine the risk level (Low, Medium, High) for takedown based on policy violations.
            
            Return JSON format:
            {{
                "risk_level": "High",
                "platform": "{req.platform}",
                "issues": [
                    {{
                        "category": "Health Claims",
                        "snippet": "exact text from transcript",
                        "rationale": "explanation",
                        "policy_citations": ["Section 3.1"]
                    }}
                ]
            }}
            """
        print(f"DEBUG: Analysis prompt: {analysis_prompt}")
        model = _ensure_gemini()
        print(f"DEBUG: Model: {model}")
        response = model.generate_content(analysis_prompt)
        print(f"DEBUG: Response: {response}")
        content = response.text
        print(f"DEBUG: Content: {content}")
    except Exception as e:
        logger.error(f"LLM Generation Error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "platform": req.platform,
            "risk_level": "Unknown",
            "issues": [{
                "category": "System Error",
                "snippet": "LLM Analysis Failed",
                "rationale": f"AI Model failed to generate response. Reason: {str(e)}",
                "policy_citations": []
            }]
        }

    # --- STEP 4: JSON Parsing ---
    # Helper to clean JSON (LLMs often add markdown backticks)
    def clean_json_text(text: str) -> str:
        text = text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            # Find the first newline
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline+1:]
        if text.endswith("```"):
            text = text[:-3]
        json_text = text.strip()
        print(f"DEBUG: Cleaned content: {json_text}")
        return json_text

    try:
        json_text = clean_json_text(content)
        result = json.loads(json_text)
        
        risk_level = result.get("risk_level", "Medium")
        issues = result.get("issues", [])        
        return {
            "platform": req.platform,
            "risk_level": risk_level,
            "issues": issues        
        }
    except Exception as json_err:
        logger.error(f"JSON Parsing failed. Content was: {content}")
        logger.error(f"JSON Error: {str(json_err)}")
        return {
            "platform": req.platform,
            "risk_level": "Unknown",
            "issues": [{
                "category": "System Error",
                "snippet": "Response Parsing Failed",
                "rationale": f"Could not parse AI response as JSON. Error: {str(json_err)}",
                "policy_citations": []
            }]
        }

# Document indexing endpoint
@app.post("/index-documents")
def index_documents():
    try:
        # Force reload of policy documents
        global policy_index
        policy_index = None
        _ensure_policy_index()
        
        return {
            "status": "success",
            "message": "Documents indexed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document indexing failed: {str(e)}")

# Stub endpoints (keeping for compatibility)
@app.post("/ingest")
def ingest_file():
    return {
        "job_id": "cs_demo_001",
        "message": "Ingest accepted (stub)"
    }

@app.post("/process/{job_id}")
def process_job(job_id: str):
    return {
        "job_id": job_id,
        "state": "queued",
        "accepted": True
    }

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    return {
        "job_id": job_id,
        "state": "done",
        "scorecard": {
            "partial_scores": {"tiktok": 0.12, "youtube": 0.08},
            "issues": [
                {
                    "t0": 12.0,
                    "t1": 14.2,
                    "category": "Misinformation",
                    "statement": "recommended amount is 1000g",
                    "policy_citations": [
                        {
                            "platform": "tiktok",
                            "ref": "policy://tiktok/misinformation/health"
                        }
                    ],
                    "remediation": "Replace with evidence-based dosage"
                }
            ]
        }
    }