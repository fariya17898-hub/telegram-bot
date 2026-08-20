import os, io, asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import google.generativeai as genai

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Live"

def run_web():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

BOT_TOKEN = "8246819713:AAFW0ILOubzVHzqOA2WIPFzaRLUvQR1Uo4w"
GEMINI_API_KEY = "AQ.Ab8RN6KYc2Ve8E1ejS3A-KE9Bq7wHIWxmpXpEzZa6h9uYgUmF7Q"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send chart screenshot")

async def analyze_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Analyzing...")
    try:
        f = await update.message.photo[-1].get_file()
        b = await f.download_as_bytearray()
        img = Image.open(io.BytesIO(b))
        res = model.generate_content(["Analyze this trading chart and give Buy/Sell signal.", img])
        await msg.edit_text(res.text)
    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_web).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_photo))
    app.run_polling()
