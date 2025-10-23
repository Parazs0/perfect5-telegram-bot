from flask import Flask, request
import requests

# === Telegram Bot Token ===
BOT_TOKEN = "8304231350:AAE8yl3_TW6M3XC3jdLZWLj8oqZTxgDGNvQ"
# === Telegram Chat ID (your personal ID or group ID) ===
CHAT_ID = "7358908977"

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return {"status": "error", "message": "No data received"}, 400

    # Message from TradingView alert
    message = data.get('message', 'No message received')

    # Send to Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"📊 TradingView Signal:\n{message}"}
    requests.post(url, json=payload)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
