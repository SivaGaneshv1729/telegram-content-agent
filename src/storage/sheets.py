import os
import json
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Cache the sheet object to avoid re-authenticating every time
_sheet_cache = None
# Cache existing source identifiers for faster idempotency checks
_id_cache = set()
_cache_initialized = False

def get_sheet():
    global _sheet_cache, _id_cache, _cache_initialized
    
    if _sheet_cache is not None:
        return _sheet_cache
        
    creds_json_str = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    
    if not creds_json_str or creds_json_str == '{"type": "service_account", ...}':
        logger.error("GOOGLE_SHEETS_CREDENTIALS_JSON is not configured properly.")
        return None
        
    if not spreadsheet_id or spreadsheet_id == 'your_google_spreadsheet_id_here':
        logger.error("SPREADSHEET_ID is not configured properly.")
        return None

    try:
        creds_dict = json.loads(creds_json_str)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Assuming the first sheet is the target
        _sheet_cache = client.open_by_key(spreadsheet_id).sheet1
        
        # Initialize headers if sheet is empty
        try:
            first_row = _sheet_cache.row_values(1)
            if not first_row:
                headers = [
                    "SourceIdentifier", "SubmissionTimestamp", "ContentType", 
                    "LLMTitle", "Rationale", "Category", "X_Variant", "LinkedIn_Variant"
                ]
                _sheet_cache.append_row(headers)
        except Exception as e:
            logger.warning(f"Could not check/set headers, sheet might be empty: {e}")
            
        return _sheet_cache
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Sheets: {e}")
        return None

def initialize_cache():
    global _id_cache, _cache_initialized
    if _cache_initialized:
        return
        
    sheet = get_sheet()
    if not sheet:
        return
        
    try:
        # Fetch the entire first column (SourceIdentifier)
        col_values = sheet.col_values(1)
        # Skip header if it exists
        if col_values and col_values[0] == "SourceIdentifier":
            col_values = col_values[1:]
        
        _id_cache = set(col_values)
        _cache_initialized = True
        logger.info(f"Initialized idempotency cache with {len(_id_cache)} entries.")
    except Exception as e:
        logger.error(f"Failed to initialize idempotency cache: {e}")

def is_duplicate(source_id: str) -> bool:
    initialize_cache()
    return source_id in _id_cache

def append_row(source_identifier: str, content_type: str, title: str, rationale: str, category: str, x_variant: str, linkedin_variant: str) -> bool:
    sheet = get_sheet()
    if not sheet:
        return False
        
    # Double check duplicate before appending just in case
    if is_duplicate(source_identifier):
        return True # Treat as success since it's already there
        
    timestamp = datetime.now(timezone.utc).isoformat()
    
    row = [
        source_identifier,
        timestamp,
        content_type,
        title,
        rationale,
        category,
        x_variant,
        linkedin_variant
    ]
    
    try:
        sheet.append_row(row)
        # Update local cache
        _id_cache.add(source_identifier)
        logger.info(f"Successfully appended row for {source_identifier}")
        return True
    except Exception as e:
        logger.error(f"Failed to append row to Google Sheets: {e}")
        return False
