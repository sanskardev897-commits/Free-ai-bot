import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

# ---- Config: environment variables theke asbe (Render e set korte hobe) ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Prottek user er jonno alada chat history rakha (simple in-memory)
user_chats = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Ami tomar AI bot. Amake je kono kotha jiggesh koro, ami reply debo."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats.pop(user_id, None)
    await update.message.reply_text("Chat history reset hoye geche.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])

    chat = user_chats[user_id]

    try:
        response = chat.send_message(user_text)
        reply_text = response.text
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        reply_text = "Dukhkhito, ekhon reply dite parlam na. Ektu por abar try koro."

    await update.message.reply_text(reply_text)


def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        raise SystemExit("TELEGRAM_TOKEN ar GEMINI_API_KEY environment variable e set korte hobe.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot chalu hoye geche...")
    app.run_polling()


if __name__ == "__main__":
    main()
