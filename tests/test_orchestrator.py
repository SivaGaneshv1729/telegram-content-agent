import pytest
import json
from unittest.mock import patch, MagicMock
from llm.orchestrator import generate_content

@patch('llm.orchestrator.groq_client')
@patch('llm.orchestrator.OLLAMA_URL', None)
def test_generate_content_success_groq(mock_groq_client):
    valid_json_response = json.dumps({
        "title": "Test Title",
        "rationale": "Test Rationale",
        "category": "Test Category",
        "variants": {
            "x_post": "Test X",
            "linkedin_post": "Test LinkedIn"
        }
    })
    
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = valid_json_response
    mock_groq_client.chat.completions.create.return_value = mock_completion
    
    result = generate_content("Raw article content")
    
    assert result['title'] == "Test Title"
    assert result['variants']['x_post'] == "Test X"
    # Ensure it only took 1 attempt
    assert mock_groq_client.chat.completions.create.call_count == 1

@patch('llm.orchestrator.groq_client')
@patch('llm.orchestrator.OLLAMA_URL', None)
@patch('llm.orchestrator.time.sleep') # mock sleep so tests run fast
def test_generate_content_retry_on_invalid_json(mock_sleep, mock_groq_client):
    invalid_json = "This is not json"
    valid_json_response = json.dumps({
        "title": "Test Title",
        "rationale": "Test Rationale",
        "category": "Test Category",
        "variants": {
            "x_post": "Test X",
            "linkedin_post": "Test LinkedIn"
        }
    })
    
    mock_completion_invalid = MagicMock()
    mock_completion_invalid.choices[0].message.content = invalid_json
    
    mock_completion_valid = MagicMock()
    mock_completion_valid.choices[0].message.content = valid_json_response
    
    # First attempt returns invalid, second returns valid
    mock_groq_client.chat.completions.create.side_effect = [mock_completion_invalid, mock_completion_valid]
    
    result = generate_content("Raw article content")
    
    assert result['title'] == "Test Title"
    assert mock_groq_client.chat.completions.create.call_count == 2
    mock_sleep.assert_called_once() # Should have slept once between retries

@patch('llm.orchestrator.groq_client')
@patch('llm.orchestrator.OLLAMA_URL', None)
@patch('llm.orchestrator.time.sleep')
def test_generate_content_max_retries(mock_sleep, mock_groq_client):
    invalid_json = "Still not json"
    
    mock_completion_invalid = MagicMock()
    mock_completion_invalid.choices[0].message.content = invalid_json
    
    # Always returns invalid
    mock_groq_client.chat.completions.create.return_value = mock_completion_invalid
    
    result = generate_content("Raw article content")
    
    assert result == {}
    assert mock_groq_client.chat.completions.create.call_count == 3
