import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from api.gateway import send_to_adam

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def handle_message(update: Update, context):
    response = await send_to_adam(
        message=update.message.text,
        user_id=str(update.effective_user.id),
        platform="telegram"
    )
    await update.message.reply_text(response["response"])

def start_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    start_bot()