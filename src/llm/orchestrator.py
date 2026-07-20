import os
import json
import logging
import time
from groq import Groq
import requests

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OLLAMA_URL = os.environ.get("OLLAMA_URL")

# Try to initialize Groq client if key is available
groq_client = None
if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
    groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an expert content strategist and copywriter.
Your task is to analyze the provided source content and generate a structured JSON object containing a title, rationale, and social media variants.

You MUST return ONLY valid JSON matching this schema exactly:
{
  "title": "A concise, compelling title for the content",
  "rationale": "A one-sentence explanation of why this content is valuable or shareable",
  "category": "A single relevant category tag (e.g., 'AI', 'Startups', 'Productivity')",
  "variants": {
    "x_post": "A short, punchy draft optimized for X, under 280 characters. MUST be different from linkedin_post.",
    "linkedin_post": "A more professional, longer-form draft for LinkedIn, possibly using bullet points. MUST be different from x_post."
  }
}
"""

def generate_with_groq(prompt: str) -> str:
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return ""

def generate_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.1",
                "system": SYSTEM_PROMPT,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return ""

def generate_content(raw_content: str, style_prompt: str = "") -> dict:
    prompt = f"Source Content:\n{raw_content}\n"
    if style_prompt:
        prompt += f"\nApply the following style guide to all generated variants: {style_prompt}"

    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"LLM Generation Attempt {attempt + 1}")
        
        # Prefer Groq if configured, fallback to Ollama
        if groq_client:
            raw_response = generate_with_groq(prompt)
        elif OLLAMA_URL:
            raw_response = generate_with_ollama(prompt)
        else:
            logger.error("No LLM backend configured. Set GROQ_API_KEY or OLLAMA_URL.")
            return {}
            
        if not raw_response:
            time.sleep(2 ** attempt) # Exponential backoff
            continue
            
        try:
            parsed = json.loads(raw_response)
            
            # Basic validation
            if "title" in parsed and "variants" in parsed and "x_post" in parsed["variants"]:
                return parsed
            else:
                logger.warning(f"JSON parsed but missing required fields: {parsed}")
                prompt += "\n\nYour previous response was missing required fields. Please ensure you strictly follow the JSON schema provided."
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}\nRaw output: {raw_response}")
            prompt += f"\n\nYour previous response was not valid JSON. Error: {e}. Please correct it and ONLY return the JSON object."
            
        time.sleep(2 ** attempt)
        
    return {}
