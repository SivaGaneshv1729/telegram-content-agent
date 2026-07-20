import os
import hashlib
import tempfile
import urllib.parse
from telegram import Update
from telegram.ext import ContextTypes
import trafilatura
from markitdown import MarkItDown

def is_url(text: str) -> bool:
    try:
        result = urllib.parse.urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

async def extract_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple[str, str, str]:
    """
    Returns a tuple: (content_type, source_id, extracted_text)
    """
    message = update.message
    
    # 1. Check if PDF document
    if message.document and message.document.mime_type == 'application/pdf':
        file = await context.bot.get_file(message.document.file_id)
        
        # Download to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_path = tmp_file.name
        
        await file.download_to_drive(tmp_path)
        
        try:
            md = MarkItDown()
            result = md.convert(tmp_path)
            extracted_text = result.text_content
            # Source ID is the hash of the original file content or the extracted text
            source_id = generate_hash(extracted_text)
            return 'pdf', source_id, extracted_text
        finally:
            os.remove(tmp_path)
            
    # 2. Check if URL or Text
    if message.text:
        text = message.text.strip()
        
        if is_url(text):
            downloaded = trafilatura.fetch_url(text)
            if downloaded:
                extracted_text = trafilatura.extract(downloaded)
                if extracted_text:
                    return 'url', text, extracted_text
            return 'url', text, "" # Failed to extract
            
        else:
            source_id = generate_hash(text)
            return 'text', source_id, text
            
    return None, None, None
