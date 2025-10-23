import os
import time
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
import threading
import http.server
import socketserver

# ✅ Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = os.getenv("CSV_PATH", "ALL_WATCHLIST_SYMBOLS.csv")

# ✅ Telegram alert function
def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
        print(f"📩 Sent alert: {message}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# ✅ Load watchlist from CSV
def load_symbols():
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found: {CSV_PATH}")
        return []
    df = pd.read_csv(CSV_PATH)
    symbols = df.iloc[:, 0].dropna().tolist()
    print(f"📈 Loaded {len(symbols)} symbols from CSV")
    return symbols

# ✅ Dummy function to simulate TradingView indicator check
# (In actual setup, this would fetch indicator values via API or scraping)
def check_indicator_signal(symbol):
    # For demo purpose, generate random fake buy/sell every few minutes
    import random
    sig = random.choice(["BUY", "SELL", "WAIT", "WAIT", "WAIT"])
    return sig

# ✅ Main loop: check all symbols, send alerts only for new signals
def monitor_signals():
    symbols = load_symbols()
    if not symbols:
        return

    last_signals = {}  # store last signal per symbol

    while True:
        for sym in symbols:
            try:
                signal = check_indicator_signal(sym)

                # only send alert if new signal detected
                if sym not in last_signals or signal != last_signals[sym]:
                    if signal in ["BUY", "SELL"]:
                        msg = f"📊 <b>{sym}</b> | <b>{signal}</b> Signal\n⏰ {datetime.now().strftime('%d-%b %H:%M')}"
                        send_telegram_alert(msg)
                    last_signals[sym] = signal

            except Exception as e:
                print(f"⚠️ Error on {sym}: {e}")

        print(f"🕒 Checking again in 2 minutes... ({datetime.now().strftime('%H:%M:%S')})")
        time.sleep(120)

# ✅ Render keep-alive (dummy web server so Render doesn’t kill the app)
def keep_alive():
    PORT = 10000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Dummy server running on port {PORT} to keep Render alive...")
        httpd.serve_forever()

# ✅ Run everything
if __name__ == "__main__":
    # start dummy web server in background
    threading.Thread(target=keep_alive, daemon=True).start()

    print("🚀 Perfect5 Telegram Bot started...")
    print("🔁 Monitoring signals automatically...\n")
    monitor_signals()
