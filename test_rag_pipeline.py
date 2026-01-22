import os
import sys

# Add the backend directory to the path so we can import the app
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.rag_service import rag_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_rag():
    print("--- Testing RAG Pipeline ---")
    
    # 1. Check if documents exist in policy_docs
    policy_docs_dir = os.path.join(os.getcwd(), "backend", "policy_docs")
    files = os.listdir(policy_docs_dir)
    print(f"Found {len(files)} files in policy_docs.")

    # 2. Test query for TikTok
    print("\nQuerying for TikTok policies...")
    tiktok_context = rag_service.query("TikTok", "What are the rules regarding violent content and weapons?")
    print(f"TikTok Context (first 500 chars):\n{tiktok_context[:500]}...")
    
    # 3. Test query for YouTube
    print("\nQuerying for YouTube policies...")
    youtube_context = rag_service.query("YouTube", "What is the policy on hate speech?")
    print(f"YouTube Context (first 500 chars):\n{youtube_context[:500]}...")

    # 4. Check if ChromaDB directory was created
    chroma_dir = os.path.join(os.getcwd(), "backend", "chroma_db")
    if os.path.exists(chroma_dir):
        print(f"\nSuccess: ChromaDB directory found at {chroma_dir}")
    else:
        print("\nWarning: ChromaDB directory not found where expected.")

if __name__ == "__main__":
    test_rag()
