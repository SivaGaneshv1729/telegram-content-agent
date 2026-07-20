import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "/app/data/agent.db")

# For local development outside docker
if not os.environ.get("DB_PATH"):
    os.makedirs("data", exist_ok=True)
    DB_PATH = "data/agent.db"

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS styles (
                    user_id INTEGER PRIMARY KEY,
                    style_prompt TEXT
                )
            ''')
            conn.commit()
        logger.info("SQLite DB initialized.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

def set_user_style(user_id: int, style_prompt: str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO styles (user_id, style_prompt)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET style_prompt = excluded.style_prompt
            ''', (user_id, style_prompt))
            conn.commit()
    except Exception as e:
        logger.error(f"Error setting user style: {e}")

def get_user_style(user_id: int) -> str:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT style_prompt FROM styles WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return ""
    except Exception as e:
        logger.error(f"Error getting user style: {e}")
        return ""
