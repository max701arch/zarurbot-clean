import os
import logging
import requests
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# Flask app
flask_app = Flask(__name__)

# Tokeni olish
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("❌ BOT_TOKEN topilmadi! Render environmentdan tekshir!")

# Logging sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# START komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["💱 Valyuta kursi", "🌤 Ob-havo"], ["🧮 Kalkulyator"]]
    await update.message.reply_text(
        "Salom! Men foydali botman 🤖\nTanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

# Ob-havo
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌤 Qaysi shahar ob-havosini bilmoqchisiz?")
    context.user_data["weather_mode"] = True

async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("weather_mode"):
        city = update.message.text
        try:
            url = f"http://wttr.in/{city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            await update.message.reply_text(f"🌤 Ob-havo: {response.text}")
        except:
            await update.message.reply_text("❌ Ob-havoni olishda xatolik!")
        context.user_data["weather_mode"] = False

# Valyuta kursi
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
        response = requests.get(url, timeout=5).json()
        rates = {c["Ccy"]: c["Rate"] for c in response}
        usd, eur, rub = rates.get("USD"), rates.get("EUR"), rates.get("RUB")

        await update.message.reply_text(
            f"💵 1 USD = {usd} so'm\n"
            f"💶 1 EUR = {eur} so'm\n"
            f"💷 1 RUB = {rub} so'm"
        )
    except:
        await update.message.reply_text("❌ Valyuta kursini olishda xatolik!")

# Kalkulyator
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧮 Masalani yozing (masalan: 25*30)")
    context.user_data["calc_mode"] = True

async def handle_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("calc_mode"):
        text = update.message.text
        try:
            if all(ch in "0123456789+-*/. " for ch in text):
                result = eval(text)
                await update.message.reply_text(f"✅ Natija: {result}")
            else:
                await update.message.reply_text("❌ Faqat son va + - * / ishlat!")
        except:
            await update.message.reply_text("❌ Noto‘g‘ri ifoda")
        context.user_data["calc_mode"] = False

# Message handler (menu)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💱 Valyuta kursi":
        await currency(update, context)
    elif text == "🌤 Ob-havo":
        await weather(update, context)
    elif text == "🧮 Kalkulyator":
        await calc(update, context)
    else:
        await handle_weather(update, context)
        await handle_calc(update, context)

# Telegram Application
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("currency", currency))
app.add_handler(CommandHandler("calc", calc))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# Flask route for webhook
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)   # 🔥 shu joy muhim
    return "OK", 200

@flask_app.route("/")
def index():
    return "🤖 Bot ishlayapti!"

# Run bot
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
