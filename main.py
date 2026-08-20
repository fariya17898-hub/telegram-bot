import io
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import google.generativeai as genai

BOT_TOKEN = "8319405587:AAF2QA9jGsXobXmS7Ct91V_h9Bd9diDu1JI"
GEMINI_API_KEY = "AQ.Ab8RN6KXwTp4zydF9clBdxvxpQrz00dAIJKjkwV3pef92GzXHw"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Please send a screenshot of your Quotex or any trading chart. The AI will analyze it and provide a signal.")

async def analyze_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔍 Analyzing chart screenshot with AI... Please wait.")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        prompt = """
        You are an expert binary options and Forex technical analyst. Analyze this trading chart image and provide a concise summary in English with:
        1. Market Trend (Upward / Downward / Sideways)
        2. Key Support & Resistance status
        3. Candle Pattern Detected
        4. Clear Signal: 🟢 CALL (UP) or 🔴 PUT (DOWN)
        5. Estimated Accuracy / Confidence level (%)
        6. Brief risk warning statement.
        Keep the formatting clean with emojis.
        """
        
        response = model.generate_content([prompt, image])
        await status_msg.edit_text(response.text, parse_mode="Markdown")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Failed to analyze the chart. Please try again.\nError: {str(e)}")

def main():
    print("Powerful AI Bot is starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).connect_timeout(30.0).read_timeout(30.0).write_timeout(30.0).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_photo))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
