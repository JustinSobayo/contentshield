from google import genai
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Initialize the Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use Gemini Flash Latest (Stable) for cost-effective multimodal analysis
MODEL_NAME = "gemini-flash-latest"

def upload_file(path_to_file: str, mime_type: str = None):
    """Uploads a file to Gemini File API."""
    try:
        # configuration for upload
        config = None
        if mime_type:
            config = {"mime_type": mime_type}
            
        file = client.files.upload(file=path_to_file, config=config)
        logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        logger.error(f"Failed to upload file to Gemini: {e}")
        raise

def wait_for_files_active(files):
    """Waits for files to be processed by Gemini."""
    logger.info("Waiting for file processing...")
    for file_obj in files:
        file = client.files.get(name=file_obj.name)
        while file.state == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = client.files.get(name=file_obj.name)
        if file.state != "ACTIVE":
            raise Exception(f"File {file.name} failed to process: {file.state}")
    logger.info("File processing complete.")

def analyze_multimodal(prompt: str, file_path: str = None, mime_type: str = None):
    """
    Analyzes content using Gemini 1.5 Flash.
    Supports text-only or multimodal (video+text) analysis.
    """
    
    contents = [prompt]
    
    uploaded_file = None
    if file_path:
        uploaded_file = upload_file(file_path, mime_type=mime_type)
        wait_for_files_active([uploaded_file])
        contents.append(uploaded_file)
        
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        
        # Cleanup uploaded file to save storage/cost if needed (optional)
        # if uploaded_file:
        #     client.files.delete(name=uploaded_file.name)
        
        return response.text
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        raise
