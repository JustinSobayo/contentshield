from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    transcript: Optional[str] = None
    platform: str
    video_filename: Optional[str] = None

class Issue(BaseModel):
    category: str
    timestamp: Optional[str] = None
    snippet: str
    rationale: str

class AnalyzeResponse(BaseModel):
    platform: str
    risk_level: str
    summary_rationale: Optional[str] = None
    issues: List[Issue]
