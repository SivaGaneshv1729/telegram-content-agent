import pytest
from unittest.mock import MagicMock, patch
from extraction.extractor import is_url, generate_hash, extract_content
import tempfile
import os

def test_is_url():
    assert is_url("https://google.com") == True
    assert is_url("http://test.com/article?id=1") == True
    assert is_url("not a url") == False
    assert is_url("google.com") == False  # No scheme

def test_generate_hash():
    text1 = "This is a test text."
    text2 = "This is a test text."
    text3 = "Different text."
    
    assert generate_hash(text1) == generate_hash(text2)
    assert generate_hash(text1) != generate_hash(text3)

@pytest.mark.asyncio
@patch('extraction.extractor.trafilatura.fetch_url')
@patch('extraction.extractor.trafilatura.extract')
async def test_extract_content_url(mock_extract, mock_fetch_url):
    # Mock update and context
    mock_update = MagicMock()
    mock_update.message.document = None
    mock_update.message.text = "https://example.com"
    
    mock_context = MagicMock()
    
    # Mock trafilatura
    mock_fetch_url.return_value = "<html>mock html</html>"
    mock_extract.return_value = "Extracted article content"
    
    content_type, source_id, extracted_text = await extract_content(mock_update, mock_context)
    
    assert content_type == 'url'
    assert source_id == "https://example.com"
    assert extracted_text == "Extracted article content"
    mock_fetch_url.assert_called_once_with("https://example.com")
    mock_extract.assert_called_once_with("<html>mock html</html>")

@pytest.mark.asyncio
async def test_extract_content_text():
    mock_update = MagicMock()
    mock_update.message.document = None
    mock_update.message.text = "This is plain text content."
    mock_context = MagicMock()
    
    content_type, source_id, extracted_text = await extract_content(mock_update, mock_context)
    
    assert content_type == 'text'
    assert extracted_text == "This is plain text content."
    assert source_id == generate_hash("This is plain text content.")

@pytest.mark.asyncio
@patch('extraction.extractor.MarkItDown')
async def test_extract_content_pdf(mock_markitdown):
    from unittest.mock import AsyncMock
    mock_update = MagicMock()
    mock_update.message.text = None
    mock_update.message.document.mime_type = 'application/pdf'
    mock_update.message.document.file_id = 'test_file_id'
    
    mock_context = MagicMock()
    mock_file = AsyncMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    
    mock_md_instance = MagicMock()
    mock_md_result = MagicMock()
    mock_md_result.text_content = "Extracted PDF content"
    mock_md_instance.convert.return_value = mock_md_result
    mock_markitdown.return_value = mock_md_instance

    content_type, source_id, extracted_text = await extract_content(mock_update, mock_context)
    
    assert content_type == 'pdf'
    assert extracted_text == "Extracted PDF content"
    assert source_id == generate_hash("Extracted PDF content")
    
    mock_context.bot.get_file.assert_called_once_with('test_file_id')
    mock_file.download_to_drive.assert_called_once()
