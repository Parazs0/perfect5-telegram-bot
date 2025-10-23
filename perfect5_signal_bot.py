import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = os.getenv("CSV_PATH", "ALL_WATCHLIST_SYMBOLS.csv")

# ✅ Telegram helper
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠️ Telegram Error: {e}")

# ✅ Load symbols
def load_symbols():
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found: {CSV_PATH}")
        return []
    df = pd.read_csv(CSV_PATH)
    return df["SYMBOL"].dropna().tolist()

# ✅ Mock signal generator (replace with actual logic)
def check_signal(symbol):
    """
    यहां आप अपने TradingView indicator signal fetching logic लगा सकते हैं।
    अभी यह सिर्फ mock random signal generate करता है।
    """
    import random
    # Example: 1% chance to trigger a signal
    return random.random() < 0.01

# ✅ Main Bot loop
def main():
    print("🤖 Perfect5 Auto Signal Bot Started — Render Mode 🌐")
    symbols = load_symbols()
    if not symbols:
        print("⚠️ No symbols found in CSV.")
        return

    print(f"📈 Loaded {len(symbols)} symbols from {CSV_PATH}")
    sent_signals = set()

    while True:
        for sym in symbols:
            if check_signal(sym) and sym not in sent_signals:
                msg = f"📊 <b>New Signal Alert</b>\nSymbol: <code>{sym}</code>"
                send_telegram_message(msg)
                print(f"✅ Alert Sent: {sym}")
                sent_signals.add(sym)
            time.sleep(1)  # to prevent spam on API

        print("⏳ Cycle complete — waiting 5 minutes before next check...")
        time.sleep(300)  # check every 5 minutes

if __name__ == "__main__":
    main()
