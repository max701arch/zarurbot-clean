import os
import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher

# Log sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Token va server URL
TOKEN = os.getenv("BOT_TOKEN")
APP_URL = "https://zarurbot.onrender.com"  # Sizning Render URL'ingiz

app = Flask(__name__)

updater = Updater(TOKEN, use_context=True)
dispatcher: Dispatcher = updater.dispatcher

# /start komandasi
def start(update: Update, context: CallbackContext):
    keyboard = [["Salom", "Qalaysan"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Assalomu alaykum! Men webhook orqali ishlayapman 🚀", reply_markup=reply_markup)

# Oddiy matnli javob
def echo(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(f"Siz yubordingiz: {text}")

# Handlerlar
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"


@app.route("/")
def index():
    return "Bot ishlayapti! 🚀"


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    updater.bot.set_webhook(f"{APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)
