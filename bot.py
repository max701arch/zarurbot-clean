import os
import logging
import requests
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Flask (Render web service uchun portni ochib turadi)
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "✅ Bot ishlayapti!"

# Tokenni environment orqali olamiz (RENDER dagi Environment Variables -> BOT_TOKEN)
TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["💱 Valyuta kursi", "☁️ Ob-havo"], ["🧮 Kalkulyator"]]
    await update.message.reply_text(
        "Salom! Quyidagilardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )

# Ob-havo komandasi (so‘rov yuborishni boshlaydi)
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Qaysi shahar ob-havosini bilmoqchisiz?")
    context.user_data["weather_mode"] = True

async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("weather_mode"):
        return
    city = update.message.text
    try:
        url = f"http://wttr.in/{city}?format=%C+%t"
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        await update.message.reply_text(f"🌤 {city} ob-havo: {resp.text}")
    except Exception:
        await update.message.reply_text("❌ Ob-havoni olishda xatolik")
    finally:
        context.user_data["weather_mode"] = False

# Valyuta komandasi
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
        resp = requests.get(url, timeout=6).json()
        rates = {c["Ccy"]: c["Rate"] for c in resp}
        usd = rates.get("USD", "—")
        eur = rates.get("EUR", "—")
        rub = rates.get("RUB", "—")
        await update.message.reply_text(f"💵 1 USD = {usd} so'm\n💶 1 EUR = {eur} so'm\n₽ 1 RUB = {rub} so'm")
    except Exception:
        await update.message.reply_text("❌ Valyuta kursini olishda xatolik")

# Kalkulyator
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Masalani yozing (masalan: 25+30)")
    context.user_data["calc_mode"] = True

async def handle_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("calc_mode"):
        return
    text = update.message.text
    try:
        # xavfsizroq tekshiruv: ruxsat etilgan belgilar ro'yxati
        allowed = "0123456789+-*/(). "
        if all(ch in allowed for ch in text):
            result = eval(text)  # oddiy holat — kichik bot uchun yetarli
            await update.message.reply_text(f"Natija: {result}")
        else:
            await update.message.reply_text("❌ Faqat son va + - * / ( ) belgilarini ishlating")
    except Exception:
        await update.message.reply_text("❌ Ifoda xatosi")
    finally:
        context.user_data["calc_mode"] = False

# Har qanday matn xabari uchun router
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    # tugmalar bilan keladigan ma'lumotlar
    if text == "💱 Valyuta kursi":
        await currency(update, context)
    elif text == "☁️ Ob-havo":
        await weather(update, context)
    elif text == "🧮 Kalkulyator":
        await calc(update, context)
    else:
        # agar biror rejimda bo'lsa uni qo'llash
        if context.user_data.get("weather_mode"):
            await handle_weather(update, context)
        elif context.user_data.get("calc_mode"):
            await handle_calc(update, context)
        else:
            await update.message.reply_text("Tushunmadim. /start ni bosing.")

# Botni ishga tushirish funksiyasi
def run_bot():
    if not TOKEN:
        logging.error("BOT_TOKEN topilmadi. Render-da Environment Variables -> BOT_TOKEN ni qo'ying.")
        return

    application = Application.builder().token(TOKEN).build()

    # handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("currency", currency))
    application.add_handler(CommandHandler("calc", calc))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    logging.info("Bot polling boshlanmoqda...")
    application.run_polling()

if __name__ == "__main__":
    # Flask serverni alohida threadda ishga tushiramiz (Render uchun portni ochadi)
    threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))),
        daemon=True,
    ).start()

    # keyin Telegram botni ishga tushiramiz (polling)
    run_bot()
