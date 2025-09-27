from fastapi import FastAPI
import os
from openai import OpenAI
# Create the FastAPI app instance
app = FastAPI()
from dotenv import load_dotenv
load_dotenv()

# Health check endpoint (so you know the server is alive)
@app.get("/healthz")
def health_check():
    return {"status": "ok"}


# Stub endpoint for ingest
@app.post("/ingest")
def ingest_file():
    return {
        "job_id": "cs_demo_001",
        "message": "Ingest accepted (stub)"
    }


# Stub endpoint for processing
@app.post("/process/{job_id}")
def process_job(job_id: str):
    return {
        "job_id": job_id,
        "state": "queued",
        "accepted": True
    }


# Stub endpoint for checking job status
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

openai_client = None
# Ensure OpenAI client is initialized
# i am going to make sure to include my api key in the .env file
# another option for me is to go in my terminal and run the command: export OPENAI_API_KEY=your_api_key
# and then run the command: source .env
# and then run the command: source .env
def _ensure_openai():
    global openai_client
    if openai_client is None:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/test-openai")
#this line is going to test the openai client
#this ensures that the openai client is initialized
def test_openai_connection():
    _ensure_openai()
    #first i have to try to get the response from the openai client
    try:
        #simple test call to verify the API key is working
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}],
            max_tokens = 10
        )
        return {
            "status": "success",
            "message": response.choices[0].message.content,
            "model_used": "gpt-4o"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
