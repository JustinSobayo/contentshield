from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import tempfile
import whisper
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Create the FastAPI app instance
app = FastAPI()

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
Settings.llm = Gemini(model="gemini-2.5-pro")
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

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
    takedown_likelihood: float
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
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-pro")

# Document processing and indexing
def _ensure_policy_index():
    global policy_index, chroma_client
    
    if policy_index is None:
        try:
            # Initialize Chroma client
            chroma_client = chromadb.PersistentClient(path="./chroma_db")#chroma client is initialized as a chromadb object so that i can make it a perstistant client such that data is stored on the disk so data survives server restarts
            chroma_collection = chroma_client.get_or_create_collection("policies")#collections used so that i can be able to have different types of data stored inside of the database as containers. for example, one container would be the user transcripts and another container would be the policy documents.
            
            # Create vector store
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Load documents if policy_docs folder exists
            if os.path.exists("policy_docs"):
                documents = SimpleDirectoryReader("policy_docs").load_data()
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

# Test OpenAI connection (now Gemini)
@app.get("/test-openai")
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

# Transcribe video endpoint
@app.post("/transcribe")
async def transcribe_video(file: UploadFile = File(...)):
    _ensure_whisper()
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Only video files are allowed")
        
        # Get file extension
        suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            path = tmp.name
        
        # Transcribe with Whisper
        result = whisper_model.transcribe(path, fp16=False)
        text = result.get("text", "").strip()
        language = result.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="No text transcribed")
        
        return {"text": text, "language": language}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

# Analyze content with RAG pipeline
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(req: AnalyzeRequest):
    """
    This function analyzes video transcripts for policy violations using RAG.
    
    Steps:
    1. Get the policy index (vector database of policy documents)
    2. Create a query engine to search the policy documents
    3. Query for relevant policies based on the transcript
    4. Build a prompt that includes both policy context and transcript
    5. Use Gemini to analyze and generate a structured response
    6. Parse the Gemini response into the required format
    7. Return the analysis result
    """
    #get the policy index (vector database of policy documents)
    try:
        policy_index = _ensure_policy_index()
        query_engine = policy_index.as_query_engine()#query engine is used to search the policy documents.
        policy_query = f"""
            Find {req.platform} policy violations that would cause video takedown.
            Analyze this content for violations: {req.transcript}
            Focus on: health claims, hate speech, advertising disclosure, misinformation.
            """
        policy_response = query_engine.query(policy_query)
        policy_content = str(policy_response)
        analysis_prompt = ff"""
            You are analyzing a video transcript for policy violations on {req.platform}.
            
            POLICY CONTEXT (retrieved from policy documents):
            {policy_context}
            
            VIDEO TRANSCRIPT:
            {req.transcript}
            
            TASK: Calculate takedown likelihood percentage (0-100) based on policy violations.
            
            Return JSON format:
            {{
                "takedown_percentage": 75,
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
        model = _ensure_gemini()
        response = model.generate_content(analysis_prompt)
        content = response.text
        import json
        try:
            result = json.loads(content)
            takedown_percentage = result.get("takedown_percentage", 0)
            issues = result.get("issues", [])
        except:
            raise HTTPException(status_code=500, detail="Analysis failed")
        return {
            "status": "success",
            "message": content,
            "takedown_percentage": takedown_percentage,
            "issues": issues        
        }
    except Exception as e:
         return {
            "platform": req.platform,
            "takedown_likelihood": 0.5,
            "issues": [{
                "category": "Analysis Error",
                "snippet": "",
                "rationale": f"Analysis failed: {str(e)}",
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