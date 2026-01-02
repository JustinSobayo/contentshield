from google import genai
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Initialize the Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Use Gemini 1.5 Flash (Stable version)
MODEL_NAME = "gemini-1.5-flash"

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
        logger.error(f"Failed to upload file to Gemini: {str(e)}")
        raise Exception(f"Upload failed: {str(e)}")

def wait_for_files_active(files):
    """Waits for files to be processed by Gemini."""
    logger.info("Waiting for file processing...")
    for file_obj in files:
        file = client.files.get(name=file_obj.name)
        start_time = time.time()
        while file.state == "PROCESSING":
            if time.time() - start_time > 300: # 5 minute timeout
                raise Exception("File processing timed out")
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
    
    if file_path:
        try:
            uploaded_file = upload_file(file_path, mime_type=mime_type)
            wait_for_files_active([uploaded_file])
            contents.append(uploaded_file)
        except Exception as e:
            raise Exception(f"Video processing error: {str(e)}")
        
    try:
        # Define safety settings to be more permissive for analysis results
        # These are to prevent the model from blocking its OWN analysis output
        # when it describes "dangerous" content it found.
        safety_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config={
                "safety_settings": safety_settings,
                "response_mime_type": "application/json"
            }
        )
        
        if not response.text:
            raise Exception("Gemini returned an empty response. This may be due to safety filters or model error.")
            
        return response.text
    except Exception as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        if "429" in str(e):
            raise Exception("Gemini API Quota exceeded. Please try again in a minute.")
        raise Exception(f"AI Model Error: {str(e)}")
