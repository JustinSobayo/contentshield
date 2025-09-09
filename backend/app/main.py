from fastapi import FastAPI

# Create the FastAPI app instance
app = FastAPI()

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
