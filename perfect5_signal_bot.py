import os
import time
import json
import pandas as pd
import requests
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = os.getenv("CSV_PATH")  # Example: /opt/render/project/src/ALL_WATCHLIST_SYMBOLS.csv
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))  # seconds

SENT_ALERTS_FILE = "sent_alerts.json"  # store already-sent alerts


# ✅ Telegram message sender
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")


# ✅ Load previous sent alerts from JSON file
def load_sent_alerts():
    if os.path.exists(SENT_ALERTS_FILE):
        with open(SENT_ALERTS_FILE, "r") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()


# ✅ Save new sent alerts to JSON file
def save_sent_alerts(alerts):
    with open(SENT_ALERTS_FILE, "w") as f:
        json.dump(list(alerts), f)


# ✅ Read CSV and generate alerts
def check_signals(sent_alerts):
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV not found: {CSV_PATH}")
        return sent_alerts

    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"⚠️ CSV read error: {e}")
        return sent_alerts

    required_cols = {"Symbol", "Signal", "Time"}
    if not required_cols.issubset(df.columns):
        print(f"⚠️ CSV missing columns: {required_cols}")
        return sent_alerts

    for _, row in df.iterrows():
        symbol = row["Symbol"]
        signal = row["Signal"]
        time_ = str(row.get("Time", ""))

        # Unique ID for each alert (Symbol + Signal + Time)
        alert_id = f"{symbol}_{signal}_{time_}"

        if alert_id not in sent_alerts:
            # New alert found 🚨
            message = f"📊 <b>{symbol}</b>\nSignal: <b>{signal}</b>\nTime: {time_}"
            send_telegram_message(message)
            print(f"✅ Sent new alert: {alert_id}")
            sent_alerts.add(alert_id)

    save_sent_alerts(sent_alerts)
    return sent_alerts


# ✅ Main Loop
def main():
    print("🤖 Perfect5 Auto Signal Bot Started (Render Mode)")
    print(f"📂 Using CSV: {CSV_PATH}")
    print("📡 Monitoring for new live alerts...\n")

    sent_alerts = load_sent_alerts()

    while True:
        sent_alerts = check_signals(sent_alerts)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
