from llama_index.core import SimpleDirectoryReader
import os

# Path to the specific file
file_path = "/Users/justins/contentshield-1/backend/policy_docs/Community Principles _ TikTok.pdf"

print(f"Attempting to load: {file_path}")

try:
    # Load the specific file
    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()

    print(f"Successfully loaded {len(documents)} document chunks/pages.")
    
    if documents:
        print("\n--- START OF PAGE 1 TEXT ---")
        print(documents[0].text[:1000]) # Print first 1000 chars
        print("--- END OF PAGE 1 TEXT ---")
    else:
        print("No documents found.")

except Exception as e:
    print(f"Error loading PDF: {e}")
