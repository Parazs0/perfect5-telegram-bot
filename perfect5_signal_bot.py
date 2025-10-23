import os
import time
import pandas as pd
import pandas_ta as ta
import yfinance as yf
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

# ✅ Calculate indicators & check Perfect5 conditions
def check_signal(symbol):
    try:
        data = yf.download(symbol, interval="30m", period="10d", progress=False)
        if data.empty:
            return "WAIT"

        df = data.copy()
        df["EMA20"] = ta.ema(df["Close"], 20)
        df["EMA50"] = ta.ema(df["Close"], 50)
        df["RSI"] = ta.rsi(df["Close"], 14)
        df["ADX"] = ta.adx(df["High"], df["Low"], df["Close"], 14)["ADX_14"]
        df["ATR"] = ta.atr(df["High"], df["Low"], df["Close"], 14)

        # === 5-Day High/Low ===
        five_day_data = yf.download(symbol, interval="1d", period="7d", progress=False)
        if not five_day_data.empty:
            five_day_high = five_day_data["High"].tail(5).max()
            five_day_low = five_day_data["Low"].tail(5).min()
            five_day_range = five_day_high - five_day_low
            level_20 = five_day_low + five_day_range * 0.20
            level_80 = five_day_high - five_day_range * 0.20
        else:
            level_20, level_80 = None, None

        close = df["Close"].iloc[-1]
        ema20 = df["EMA20"].iloc[-1]
        ema50 = df["EMA50"].iloc[-1]
        adx = df["ADX"].iloc[-1]
        rsi = df["RSI"].iloc[-1]

        prev_close = df["Close"].iloc[-2]
        prev_ema20 = df["EMA20"].iloc[-2]

        # === BUY / SELL logic (same as Pine Script) ===
        crossover = prev_close < prev_ema20 and close > ema20
        crossunder = prev_close > prev_ema20 and close < ema20

        buy_condition = (
            crossover and adx > 25 and rsi > 50 and (level_20 is not None and close > level_20)
        )

        sell_condition = (
            crossunder and adx > 25 and rsi < 50 and (level_80 is not None and close < level_80)
        )

        if buy_condition:
            return "BUY"
        elif sell_condition:
            return "SELL"
        else:
            return "WAIT"

    except Exception as e:
        print(f"⚠️ Error fetching {symbol}: {e}")
        return "WAIT"

# ✅ Main monitoring loop
def monitor_signals():
    symbols = load_symbols()
    if not symbols:
        return

    last_signals = {}

    while True:
        for sym in symbols:
            signal = check_signal(sym)

            if sym not in last_signals or signal != last_signals[sym]:
                if signal in ["BUY", "SELL"]:
                    msg = f"📊 <b>{sym}</b> | <b>{signal}</b> Signal\n⏰ {datetime.now().strftime('%d-%b %H:%M')}"
                    send_telegram_alert(msg)
                last_signals[sym] = signal

        print(f"🕒 Checking again in 5 minutes... ({datetime.now().strftime('%H:%M:%S')})")
        time.sleep(300)  # every 5 minutes

# ✅ Keep-alive server for Render
def keep_alive():
    PORT = 10000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ Dummy server running on port {PORT} to keep Render alive...")
        httpd.serve_forever()

# ✅ Start the bot
if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    print("🚀 Perfect5 Telegram Bot started...")
    monitor_signals()
