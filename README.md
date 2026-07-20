# Multi-Format Telegram Content Agent

A sophisticated, multi-format content ingestion agent operating via Telegram. This bot accepts content in plain text, web links, and PDF documents, processes it using Large Language Models (LLMs like Ollama/Groq) for intelligent structuring, and logs the drafts into a Google Sheet.

## Features
- **Multi-Format Ingestion**: Parses Text, URLs (via `trafilatura`), and PDFs (via `markitdown`).
- **Idempotent Writes**: Prevents duplicate entries to Google Sheets by verifying source identifiers.
- **Persistent Style Memory**: Stores user-defined style instructions in SQLite.
- **Schema-Constrained Generation**: Uses LLMs to generate titles, rationales, and social media variants (X, LinkedIn).

## Setup Instructions

1. Clone this repository.
2. Rename `.env.example` to `.env` and fill in your credentials.
3. Make sure to share your target Google Sheet with your service account email.
4. Run `docker-compose up --build -d` to start the bot.
