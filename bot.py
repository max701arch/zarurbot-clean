from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import os

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")  # Renderda Environment Variable sifatida qo‘yasiz

# /start komandasi
def start(update: Update, context: CallbackContext):
    keyboard = [["Salom", "Qalaysan"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Assalomu alaykum! Men ishga tushdim 🚀", reply_markup=reply_markup)

# Oddiy matnli xabarlarni qaytaruvchi handler
def echo(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(f"Siz yubordingiz: {text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komandalar
    dp.add_handler(CommandHandler("start", start))

    # Matnli xabarlar
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Botni ishga tushirish
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
