import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CSV_PATH = os.getenv("CSV_PATH", "/opt/render/project/src/ALL_WATCHLIST_SYMBOLS.csv")

# ----------------------------
# Telegram Function
# ----------------------------
def send_telegram_message(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("⚠️ Telegram error:", e)

# ----------------------------
# Read CSV and extract alerts
# ----------------------------
def get_alerts_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if "ALERT" in df.columns:
            alerts = df["ALERT"].dropna().astype(str).tolist()
        elif "SYMBOL" in df.columns:
            alerts = df["SYMBOL"].dropna().astype(str).tolist()
        else:
            alerts = []
        return alerts
    except Exception as e:
        print("⚠️ CSV read error:", e)
        return []

# ----------------------------
# Main Logic
# ----------------------------
def main():
    print("🚀 Perfect5 Live Alert Bot Started (Render Free Mode)")
    print(f"📂 CSV Path: {CSV_PATH}")

    last_seen = set()  # Memory of alerts already sent

    # Initial warm-up (ignore old alerts)
    print("⏳ Initial scan... ignoring old alerts.")
    last_seen.update(get_alerts_from_csv(CSV_PATH))

    while True:
        try:
            alerts = get_alerts_from_csv(CSV_PATH)
            new_alerts = [a for a in alerts if a not in last_seen]

            for alert in new_alerts:
                msg = f"📢 New Perfect5 Signal: {alert}"
                print(msg)
                send_telegram_message(msg)
                last_seen.add(alert)

            time.sleep(10)  # Every 10 seconds check again

        except Exception as e:
            print("❌ Error in loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
