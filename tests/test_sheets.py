import pytest
from unittest.mock import patch, MagicMock
import storage.sheets as sheets

@patch('storage.sheets.get_sheet')
def test_is_duplicate(mock_get_sheet):
    # Setup mock sheet
    mock_sheet = MagicMock()
    mock_sheet.col_values.return_value = ["SourceIdentifier", "hash1", "hash2"]
    mock_get_sheet.return_value = mock_sheet
    
    # Reset internal cache state for test
    sheets._cache_initialized = False
    sheets._id_cache = set()
    
    assert sheets.is_duplicate("hash1") == True
    assert sheets.is_duplicate("hash3") == False
    
    # Should be cached now, let's verify mock was only called once for init
    mock_sheet.col_values.assert_called_once()
    
    assert sheets.is_duplicate("hash2") == True
    # Still only called once
    mock_sheet.col_values.assert_called_once()

@patch('storage.sheets.get_sheet')
def test_append_row_duplicate(mock_get_sheet):
    mock_sheet = MagicMock()
    mock_sheet.col_values.return_value = ["SourceIdentifier", "existing_id"]
    mock_get_sheet.return_value = mock_sheet
    
    sheets._cache_initialized = False
    sheets._id_cache = set()
    
    # Attempting to append an existing row should return True but not call append_row
    result = sheets.append_row("existing_id", "text", "Title", "Rat", "Cat", "X", "LI")
    
    assert result == True
    mock_sheet.append_row.assert_not_called()

@patch('storage.sheets.get_sheet')
def test_append_row_success(mock_get_sheet):
    mock_sheet = MagicMock()
    mock_sheet.col_values.return_value = ["SourceIdentifier", "existing_id"]
    mock_get_sheet.return_value = mock_sheet
    
    sheets._cache_initialized = False
    sheets._id_cache = set()
    
    result = sheets.append_row("new_id", "text", "Title", "Rat", "Cat", "X", "LI")
    
    assert result == True
    mock_sheet.append_row.assert_called_once()
    assert "new_id" in sheets._id_cache
