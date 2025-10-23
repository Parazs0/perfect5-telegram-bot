# file: fno_scanner_yf.py
import warnings
warnings.filterwarnings("ignore")
import time
import math
import requests
import yfinance as yf
import ta
import pandas as pd
from datetime import datetime, timedelta

# ------------------------------
# Step 1: NSE F&O symbol list
# ------------------------------
fno_symbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN",
    "AXISBANK", "HDFC", "LT", "ITC", "MARUTI", "ONGC", "BAJFINANCE",
    "ADANIENT", "ADANIPORTS", "COALINDIA", "POWERGRID", "HCLTECH",
    "TITAN", "WIPRO"
]

# ------------------------------
# Step 2: Fetch latest prices
# ------------------------------
data = []
for symbol in fno_symbols:
    ticker = yf.Ticker(symbol + ".NS")
    hist = ticker.history(period="1d", interval="5m")
    if not hist.empty:
        last_price = hist["Close"].iloc[-1]
        data.append({"Symbol": symbol, "Last Price": round(last_price, 2)})
    else:
        data.append({"Symbol": symbol, "Last Price": None})

df = pd.DataFrame(data)
print(df)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8304231350:AAE8yl3_TW6M3XC3jdLZWLj8oqZTxgDGNvQ"
CHAT_ID = "7358908977"

INTRADAY_INTERVAL = "30m"
INTRADAY_PERIOD = "7d"
DAILY_PERIOD = "10d"

BATCH_SIZE = 15
SLEEP_BETWEEN_BATCHES = 5
ADX_THRESHOLD = 25
RSI_LEN = 14
ATR_LEN = 14
EMA20 = 20
EMA50 = 50
DAYS_BACK = 5

# ---------------- HELPERS ----------------
def ist_now_str(ts=None):
    if ts is None:
        ts = datetime.utcnow()
    if isinstance(ts, (float, int)):
        ts = datetime.utcfromtimestamp(ts)
    ist = ts + timedelta(hours=5, minutes=30)
    return ist.strftime("%d-%b %H:%M")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("Telegram send error:", e)
        return False

# ---------------- INDICATOR FUNCTIONS ----------------
def compute_indicators(df):
    df = df.copy()
    df.columns = [c.capitalize() for c in df.columns]  # Normalize column names
    try:
        df["ema20"] = ta.trend.ema_indicator(df["Close"], window=EMA20)
        df["ema50"] = ta.trend.ema_indicator(df["Close"], window=EMA50)
        df["adx"] = ta.trend.adx(df["High"], df["Low"], df["Close"], window=14)
        df["atr"] = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"], window=ATR_LEN)
        df["rsi"] = ta.momentum.rsi(df["Close"], window=RSI_LEN)
    except Exception as e:
        print("Indicator error:", e)
    return df

def compute_5day_levels(daily_df):
    highs = daily_df["High"].tail(DAYS_BACK)
    lows = daily_df["Low"].tail(DAYS_BACK)
    if len(highs) < 1 or len(lows) < 1:
        return (None, None, None, None, None)
    five_high = highs.max()
    five_low = lows.min()
    rng = five_high - five_low if (five_high is not None and five_low is not None) else None
    if rng is None or rng == 0:
        return (five_high, five_low, None, None, None)
    level_80 = five_high - rng * 0.20
    level_50 = five_low + rng * 0.50
    level_20 = five_low + rng * 0.20
    return (five_high, five_low, level_20, level_50, level_80)

def check_signal(symbol, intraday_df, daily_df):
    try:
        df = compute_indicators(intraday_df)
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else last

        ema20 = last["ema20"]
        ema50 = last["ema50"]
        adx_val = last["adx"]
        rsi_val = last["rsi"]
        atr_val = last["atr"]
        close_price = last["Close"]

        five_high, five_low, level_20, level_50, level_80 = compute_5day_levels(daily_df)

        buy_condition = False
        sell_condition = False

        if pd.notna(ema20) and pd.notna(ema50):
            prev_ema20 = prev["ema20"] if "ema20" in prev else None
            prev_ema50 = prev["ema50"] if "ema50" in prev else None

            if prev_ema20 is not None and prev_ema50 is not None:
                # EMA crossover logic
                if prev_ema20 <= prev_ema50 and ema20 > ema50:
                    if adx_val > ADX_THRESHOLD and rsi_val > 50 and (level_20 is None or close_price > level_20):
                        buy_condition = True
                elif prev_ema20 >= prev_ema50 and ema20 < ema50:
                    if adx_val > ADX_THRESHOLD and rsi_val < 50 and (level_80 is None or close_price < level_80):
                        sell_condition = True

        if buy_condition:
            sl = close_price - (atr_val * 1.5)
            tgt = close_price + (atr_val * 3.0)
            return ("BUY", close_price, sl, tgt, adx_val, rsi_val)
        elif sell_condition:
            sl = close_price + (atr_val * 1.5)
            tgt = close_price - (atr_val * 3.0)
            return ("SELL", close_price, sl, tgt, adx_val, rsi_val)
        else:
            return (None,)*6
    except Exception as e:
        print(f"Signal check error for {symbol}: {e}")
        return (None,)*6

# ---------------- MAIN SCANNER ----------------
def load_fno_list(local_file="fno_list.csv"):
    try:
        df = pd.read_csv(local_file, header=None)
        syms = df[0].astype(str).str.strip().tolist()
        print(f"Loaded {len(syms)} symbols from {local_file}")
        return syms
    except Exception as e:
        print("Could not load local FNO list:", e)
        print("Please prepare a CSV 'fno_list.csv' with one symbol per line (e.g. RELIANCE)")
        return []

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def run_scan_once(symbols):
    results = []
    yf_symbols = [s + ".NS" for s in symbols]

    for batch in chunk_list(yf_symbols, BATCH_SIZE):
        try:
            data = yf.download(tickers=batch, period=INTRADAY_PERIOD, interval=INTRADAY_INTERVAL, group_by="ticker", threads=True, progress=False, auto_adjust=False)
            daily_data = yf.download(tickers=batch, period=DAILY_PERIOD, interval="1d", group_by="ticker", threads=True, progress=False, auto_adjust=False)
        except Exception as e:
            print("yfinance download error:", e)
            time.sleep(2)
            continue

        for original_sym in batch:
            sym = original_sym.replace(".NS", "")
            try:
                intraday_df = data[original_sym] if isinstance(data.columns, pd.MultiIndex) else data
                daily_df = daily_data[original_sym] if isinstance(daily_data.columns, pd.MultiIndex) else daily_data

                if intraday_df.empty:
                    continue

                sig, price, sl, tgt, adx, rsi = check_signal(sym, intraday_df, daily_df)
                if sig is not None:
                    tmsg = (
                        f"*{sig} Signal Triggered!*\n"
                        f"Ticker: {sym}\n"
                        f"Price: {price:.2f}\n"
                        f"SL: {sl:.2f}\n"
                        f"TGT: {tgt:.2f}\n"
                        f"ADX: {adx:.2f}\n"
                        f"RSI: {rsi:.2f}\n"
                        f"Time (IST): {ist_now_str()}"
                    )
                    print("Signal:", tmsg)
                    send_telegram(tmsg)
                    results.append((sym, sig, price, sl, tgt))
            except Exception as e:
                print("Error processing", sym, e)
                continue

        time.sleep(SLEEP_BETWEEN_BATCHES)

    return results

if __name__ == "__main__":
    symbols = load_fno_list(r"C:\Users\Gandhi\Documents\fno_list.csv")
    if not symbols:
        print("No symbols to scan. Edit fno_list.csv to add F&O underlyings (without .NS). Exiting.")
        exit(1)

    print(f"Starting single scan run for {len(symbols)} symbols...")
    found = run_scan_once(symbols)
    print("Scan complete. Signals found:", found)
