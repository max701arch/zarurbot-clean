import os
import logging
import requests
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import threading

# 🔹 Flask server (Render port ochilishini ta’minlash uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot ishlayapti!"

# 🔹 Token environment’dan olinadi
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["💵 Valyuta kursi", "🌤 Ob-havo"]]
    await update.message.reply_text(
        "Salom! Men foydali botman 🤖\nQuyidagidan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

# 🌤 Ob-havo komandasi
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Qaysi shahar ob-havosini bilmoqchisiz?")
    context.user_data["weather_mode"] = True

async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("weather_mode"):
        city = update.message.text
        try:
            url = f"http://wttr.in/{city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            await update.message.reply_text(f"🌤 {city} ob-havosi: {response.text}")
        except Exception:
            await update.message.reply_text("❌ Ob-havoni olishda muammo!")
        context.user_data["weather_mode"] = False

# 💵 Valyuta komandasi
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
        response = requests.get(url, timeout=5).json()
        rates = {c["Ccy"]: c["Rate"] for c in response}
        usd = rates.get("USD")
        eur = rates.get("EUR")
        rub = rates.get("RUB")
        await update.message.reply_text(
            f"💵 1 USD = {usd} so'm\n"
            f"💶 1 EUR = {eur} so'm\n"
            f"₽ 1 RUB = {rub} so'm"
        )
    except Exception:
        await update.message.reply_text("❌ Valyuta kursini olishda muammo!")

# 🔹 Botni ishga tushirish
def run_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("currency", currency))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weather))

    application.run_polling()

if __name__ == "__main__":
    # Flask serverni alohida threadda ishga tushiramiz
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    ).start()

    # Telegram botni ishga tushiramiz
    run_bot()
