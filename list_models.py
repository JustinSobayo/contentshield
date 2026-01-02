from google import genai
import os
from dotenv import load_dotenv

# Load env to get API key
load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    load_dotenv(".env")
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    print("Listing available models...")
    for model in client.models.list():
        print(f"Name: {model.name}, Display Name: {model.display_name}")
except Exception as e:
    print(f"Failed to list models: {e}")
