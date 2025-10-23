from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === Replace with your bot token ===
BOT_TOKEN = "8304231350:AAE8yl3_TW6M3XC3jdLZWLj8oqZTxgDGNvQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 MyPerfect5Bot is now active and connected!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
