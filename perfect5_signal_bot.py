import os
import time
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === Load ENV ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = os.getenv("CSV_PATH", "ALL_WATCHLIST_SYMBOLS.csv")

# === Telegram send ===
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# === Load watchlist ===
def load_symbols():
    if not os.path.exists(CSV_PATH):
        print("❌ CSV not found:", CSV_PATH)
        return []
    df = pd.read_csv(CSV_PATH)
    symbols = df.iloc[:, 0].dropna().tolist()
    return symbols

# === Selenium Setup ===
def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

# === Get indicator signal from chart ===
def get_indicator_signal(driver, symbol):
    url = f"https://www.tradingview.com/chart/?symbol={symbol}"
    driver.get(url)
    time.sleep(8)  # wait for chart + indicator to load

    # Perfect5 indicator labels contain "BUY @", "SELL @" in label text
    page_source = driver.page_source
    if "BUY @" in page_source:
        return "BUY"
    elif "SELL @" in page_source:
        return "SELL"
    else:
        return "WAIT"

# === Main ===
def main():
    symbols = load_symbols()
    if not symbols:
        return

    print(f"📈 Loaded {len(symbols)} symbols from CSV")
    driver = setup_driver()

    print("🔑 Please login to TradingView manually once...")
    driver.get("https://www.tradingview.com/chart/")
    input("➡️ Login करें और जब chart + Perfect5 indicator दिखे तब Enter दबाएँ...")

    last_alerts = {}

    while True:
        print(f"\n⏰ Checking signals... ({datetime.now().strftime('%H:%M:%S')})")
        for sym in symbols:
            try:
                signal = get_indicator_signal(driver, sym)
                if sym not in last_alerts or last_alerts[sym] != signal:
                    if signal in ["BUY", "SELL"]:
                        msg = f"🚀 <b>{sym}</b>\n📊 Perfect5 Signal: <b>{signal}</b>\n🕒 {datetime.now().strftime('%d-%b %H:%M')}"
                        send_telegram(msg)
                        print(f"✅ Alert sent for {sym}: {signal}")
                    last_alerts[sym] = signal
                else:
                    print(f"⏸️ {sym} — no change ({signal})")
            except Exception as e:
                print(f"⚠️ Error on {sym}: {e}")

        print("🕐 Sleeping 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    main()
