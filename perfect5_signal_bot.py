import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed, Interval
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
import requests
import threading
import http.server
import socketserver

# ===========================
# 🔹 Load environment
# ===========================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TV_USERNAME = os.getenv("TV_USERNAME")
TV_PASSWORD = os.getenv("TV_PASSWORD")

# ===========================
# 🔹 TradingView Login
# ===========================
try:
    tv = TvDatafeed(username=TV_USERNAME, password=TV_PASSWORD)
    print("✅ TradingView login successful.")
except Exception as e:
    print(f"⚠️ Login error: {e}")
    tv = TvDatafeed(nologin=True)

# ===========================
# 🔹 Load CSV
# ===========================
CSV_PATH = r"ALL_WATCHLIST_SYMBOLS.csv"
symbols_df = pd.read_csv(CSV_PATH)
symbols = symbols_df["SYMBOL"].dropna().unique().tolist()
print(f"📈 Loaded {len(symbols)} symbols from CSV")

# ===========================
# 🔹 Telegram Function
# ===========================
def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram config missing")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# ===========================
# 🔹 Exchange & Market Hours
# ===========================
MARKET_HOURS = {
    "NSE": ("09:15", "15:30"),
    "BSE": ("09:15", "15:30"),
    "MCX": ("09:00", "24:00"),
    "INDEX": ("00:00", "23:59"),
    "CAPITALCOM": ("00:00", "23:59"),
    "TVC": ("00:00", "23:59"),
    "IG": ("00:00", "23:59"),
    "OANDA": ("00:00", "23:59"),
    "SKILLING": ("00:00", "23:59"),
    "SPREADEX": ("00:00", "23:59"),
    "SZSE": ("00:00", "23:59"),
    "VANTAGE": ("00:00", "23:59")
}

def detect_exchange(symbol):
    """Auto detect exchange name based on symbol or CSV column"""
    if "EXCHANGE" in symbols_df.columns:
        return symbols_df.loc[symbols_df["SYMBOL"] == symbol, "EXCHANGE"].values[0]

    # Guess based on name pattern
    if symbol.endswith(".NS"):
        return "NSE"
    elif symbol.endswith(".BO"):
        return "BSE"
    elif "CRUDE" in symbol or "GOLD" in symbol or "SILVER" in symbol:
        return "MCX"
    elif any(x in symbol for x in ["USD", "OIL", "EUR", "BTC", "INDEX"]):
        return "INDEX"
    else:
        return "NSE"  # Default fallback

def is_market_open(exchange):
    """Check if current time is within market hours"""
    now = datetime.now().time()
    day = datetime.now().strftime("%A")

    # Skip weekends
    if day in ["Saturday", "Sunday"]:
        return False

    start, end = MARKET_HOURS.get(exchange, ("00:00", "23:59"))
    return start <= now.strftime("%H:%M") <= end

# ===========================
# 🔹 Signal Logic
# ===========================
def calculate_signals(symbol):
    try:
        exchange = detect_exchange(symbol)

        # Market hours check
        if not is_market_open(exchange):
            print(f"⏸️ Market closed for {symbol} ({exchange})")
            return

        df = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_30_minute, n_bars=100)
        if df is None or df.empty:
            print(f"⚠️ No data for {symbol} ({exchange})")
            return

        df = df.reset_index()
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["high"] = pd.to_numeric(df["high"], errors="coerce")
        df["low"] = pd.to_numeric(df["low"], errors="coerce")
        df.dropna(inplace=True)

        if len(df) < 50:
            return

        # Indicators
        ema20 = EMAIndicator(df["close"], window=20).ema_indicator()
        adx_val = ADXIndicator(df["high"], df["low"], df["close"], window=14).adx()
        rsi_val = RSIIndicator(df["close"], window=14).rsi()

        level_20 = float(df["close"].quantile(0.2))
        level_80 = float(df["close"].quantile(0.8))
        adx_threshold = 25

        close_now = df["close"].iloc[-1]
        ema_now = ema20.iloc[-1]
        adx_now = adx_val.iloc[-1]
        rsi_now = rsi_val.iloc[-1]

        # Conditions
        buy_condition = close_now > ema_now and adx_now > adx_threshold and rsi_now > 50 and close_now > level_20
        sell_condition = close_now < ema_now and adx_now > adx_threshold and rsi_now < 50 and close_now < level_80

        # Signal file tracking
        signal_file = "signal_log.txt"
        last_signal = ""
        if os.path.exists(signal_file):
            with open(signal_file, "r") as f:
                last_signal = f.read().strip()

        new_signal = ""
        if buy_condition:
            new_signal = f"🟢 BUY SIGNAL — {symbol} ({exchange})\n💰 {round(close_now,2)} | RSI {round(rsi_now,1)} | ADX {round(adx_now,1)}"
        elif sell_condition:
            new_signal = f"🔴 SELL SIGNAL — {symbol} ({exchange})\n💰 {round(close_now,2)} | RSI {round(rsi_now,1)} | ADX {round(adx_now,1)}"

        if new_signal and new_signal != last_signal:
            print(new_signal)
            send_telegram_message(new_signal)
            with open(signal_file, "w") as f:
                f.write(new_signal)
        else:
            print(f"✅ {symbol} ({exchange}) — No signal")

    except Exception as e:
        print(f"⚠️ Error in {symbol}: {e}")

# ===========================
# 🔹 Keep Alive (for Render)
# ===========================
def keep_alive():
    PORT = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Keep-alive server running on port {PORT}")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# ===========================
# 🔹 Main Loop
# ===========================
print(f"\n🔁 Monitoring {len(symbols)} symbols automatically...\n")

while True:
    print(f"\n🕒 Scanning at {datetime.now().strftime('%H:%M:%S')}\n")
    for symbol in symbols:
        calculate_signals(symbol)
        time.sleep(5)
    print("\n🔄 Full scan complete — waiting 2 minutes...\n")
    time.sleep(120)
