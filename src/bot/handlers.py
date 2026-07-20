import logging
from telegram import Update
from telegram.ext import ContextTypes
from storage.memory import set_user_style, get_user_style
from storage.sheets import append_row, is_duplicate
from extraction.extractor import extract_content
from llm.orchestrator import generate_content

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the Content Team Agent! Send me text, links, or PDFs, and I'll process them for you.")

async def setstyle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # The style description is everything after /setstyle
    style_description = " ".join(context.args)
    
    if not style_description:
        await update.message.reply_text("Please provide a style description. Example: /setstyle Be witty and use emojis.")
        return
        
    set_user_style(user_id, style_description)
    await update.message.reply_text(f"Style preference saved: '{style_description}'")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    try:
        # 1. Extraction
        content_type, source_id, raw_content = await extract_content(update, context)
        
        if not raw_content:
            await update.message.reply_text("Could not extract content from the message.")
            return

        # 2. Idempotency Check
        if is_duplicate(source_id):
            logger.info(f"Duplicate content detected: {source_id}")
            # The instructions say: "The second submission should be either ignored or handled without creating a new content entry."
            # So we can just silently ignore or reply. Let's reply so the user knows.
            await update.message.reply_text("This content has already been processed.")
            return

        # 3. LLM Processing
        style_prompt = get_user_style(user_id)
        
        processing_message = await update.message.reply_text("Processing content...")
        
        structured_data = generate_content(raw_content, style_prompt)
        
        if not structured_data:
            await processing_message.edit_text("Failed to process content with LLM after multiple retries.")
            return
            
        # 4. Save to Google Sheets
        success = append_row(
            source_identifier=source_id,
            content_type=content_type,
            title=structured_data.get('title', ''),
            rationale=structured_data.get('rationale', ''),
            category=structured_data.get('category', ''),
            x_variant=structured_data.get('variants', {}).get('x_post', ''),
            linkedin_variant=structured_data.get('variants', {}).get('linkedin_post', '')
        )
        
        if success:
            await processing_message.edit_text(f"Successfully processed and logged to Google Sheets!\n\n**Title**: {structured_data.get('title')}")
        else:
            await processing_message.edit_text("Failed to write to Google Sheets. Check logs.")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while processing your request.")
