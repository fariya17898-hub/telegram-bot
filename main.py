import os
import io
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import google.generativeai as genai

# --- 1. HEALTH CHECK SERVER (To prevent Render timeouts) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running live!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 2. CONFIGURATION ---
BOT_TOKEN = "8319405587:AAFWHr8QY47VFxnyemyNll0vllP9rxk4uEs"
GEMINI_API_KEY = "AQ.Ab8RN6KYc2Ve8E1ejS3A-KE9Bq7wHIWxmpXpEzZa6h9uYgUmF7Q"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. TELEGRAM BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send a screenshot of your chart for analysis.")

async def analyze_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 Analyzing chart screenshot with AI... Please wait.")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        prompt = (
            "Analyze this trading chart. Identify the trend, key support and resistance levels, "
            "and give a clear Buy/Sell suggestion with confidence percentage."
        )
        
        response = model.generate_content([prompt, image])
        await status_msg.edit_text(response.text)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Failed to analyze the chart.\nError: {str(e)}")

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    # Start web server in background
    Thread(target=run_web).start()
    
    # Start Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_photo))
    
    print("Bot is starting...")
    app.run_polling()
