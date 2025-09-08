import os
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Tokenni faqat Environment Variable orqali olish
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# START komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["💵 Valyuta kursi", "☁️ Ob-havo"], ["🧮 Kalkulyator"]]
    await update.message.reply_text(
        "Salom! Men foydali botman 🤖\nTanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

# Ob-havo
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏙️ Qaysi shahar ob-havosini bilmoqchisiz?")
    context.user_data["weather_mode"] = True

async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    try:
        url = f"http://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        await update.message.reply_text(f"☁️ Ob-havo: {response.text}")
    except Exception:
        await update.message.reply_text("❌ Ob-havoni olishda xatolik!")
    context.user_data["weather_mode"] = False

# Valyuta kursi
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
            f"💴 1 RUB = {rub} so'm"
        )
    except Exception:
        await update.message.reply_text("❌ Valyuta kursini olishda xatolik")

# Kalkulyator
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧮 Masalani yozing (masalan: 25*30)")
    context.user_data["calc_mode"] = True

async def handle_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("calc_mode"):
        return
    text = update.message.text
    try:
        if all(ch in "0123456789+-*/. " for ch in text):
            result = eval(text)
            await update.message.reply_text(f"✅ Natija: {result}")
        else:
            await update.message.reply_text("❌ Faqat son va + - * / ishlating!")
    except Exception:
        await update.message.reply_text("❌ Noto‘g‘ri ifoda")
    context.user_data["calc_mode"] = False

# Bosh menu handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "💵 Valyuta kursi":
        await currency(update, context)
    elif text == "☁️ Ob-havo":
        await weather(update, context)
    elif text == "🧮 Kalkulyator":
        await calc(update, context)
    else:
        if context.user_data.get("weather_mode"):
            await handle_weather(update, context)
        elif context.user_data.get("calc_mode"):
            await handle_calc(update, context)

# Asosiy funksiya
def main():
    if not TOKEN:
        print("❌ BOT_TOKEN topilmadi! Render environmentni tekshiring.")
        return

    app = Application.builder().token(TOKEN).build()

    # Handlers qo‘shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("currency", currency))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot ishga tushmoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()
