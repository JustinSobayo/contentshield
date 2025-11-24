import os
import sys
from unittest.mock import MagicMock
from llama_index.core.llms import LLM, CustomLLM
from llama_index.core.base.embeddings.base import BaseEmbedding

# Define a Mock LLM that satisfies isinstance(llm, LLM)
class MockGemini(CustomLLM):
    def complete(self, prompt, **kwargs):
        return "Mock response"
    
    def stream_complete(self, prompt, **kwargs):
        pass

    @property
    def metadata(self):
        return MagicMock()

# Define a Mock Embedding that satisfies isinstance(embed_model, BaseEmbedding)
class MockEmbedding(BaseEmbedding):
    def _get_query_embedding(self, query):
        return [0.1] * 768
    
    async def _aget_query_embedding(self, query):
        return [0.1] * 768

    def _get_text_embedding(self, text):
        return [0.1] * 768

# Mock the module
mock_gemini_module = MagicMock()
mock_gemini_module.Gemini = MockGemini
sys.modules["llama_index.llms.gemini"] = mock_gemini_module

mock_embedding_module = MagicMock()
mock_embedding_module.GeminiEmbedding = MockEmbedding
sys.modules["llama_index.embeddings.gemini"] = mock_embedding_module

os.environ["GOOGLE_API_KEY"] = "dummy_key"
os.environ["GEMINI_API_KEY"] = "dummy_key"

from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_rate_limit():
    print("Testing rate limit on /transcribe endpoint...")
    
    # The limit is 5/minute. Let's try to hit it 7 times.
    for i in range(1, 8):
        # We use a dummy file for the transcribe endpoint
        files = {'file': ('test.mp4', b'dummy content', 'video/mp4')}
        
        # Note: We expect 400 or 500 for the first few because we aren't mocking Whisper,
        # but that counts as a "request" for the rate limiter.
        # The 6th and 7th requests should return 429.
        try:
            response = client.post("/transcribe", files=files)
            print(f"Request {i}: Status Code {response.status_code}")
            
            if response.status_code == 429:
                print("Rate limit triggered successfully!")
                return
        except Exception as e:
            print(f"Request {i}: Error {e}")
            
    print("Rate limit was NOT triggered.")

if __name__ == "__main__":
    test_rate_limit()
