import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle # Pickle module import करें

# 🧭 आपकी सभी watchlist links यहाँ डालें
WATCHLIST_URLS = [
    "https://www.tradingview.com/watchlists/171173553/",
    # ... बाकी watchlist links
]

def extract_symbols_from_html(html):
    """Extracts symbols from TradingView HTML source."""
    pattern = r'/symbols/([A-Za-z0-9:_\-\!]+)/'
    matches = re.findall(pattern, html)
    symbols = []
    for s in matches:
        s = s.upper()
        s = s.replace('NSE-', 'NSE:').replace('BSE-', 'BSE:').replace('MCX-', 'MCX:')
        s = s.replace('--', '-')
        if s not in symbols:
            symbols.append(s)
    return symbols

def main():
    print("🔥 TradingView Multi-Watchlist Exporter — v6.0 (NSE + MCX + FX Supported)\n")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    all_symbols = []

    for url in WATCHLIST_URLS:
        print(f"🌐 Opening: {url}")
        driver.get(url)
        print("🔑 Login करें अगर जरूरत हो, और watchlist load होने के बाद Enter दबाएँ...")
        input("⏸️ Press Enter when symbols are visible...\n")

        html = driver.page_source
        symbols = extract_symbols_from_html(html)
        print(f"✅ Found {len(symbols)} symbols in this watchlist.\n")
        all_symbols.extend(symbols)

    # Remove duplicates
    unique_symbols = sorted(set(all_symbols))

    if unique_symbols:
        filename = "ALL_WATCHLIST_SYMBOLS.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SYMBOL'])
            for sym in unique_symbols:
                writer.writerow([sym])

        print(f"\n🎉 Export Complete! Total unique symbols: {len(unique_symbols)}")
        print(f"💾 File saved: {filename}")
        print("📂 Location: C:\\Users\\Gandhi\\Documents\\")
    else:
        print("⚠️ कोई symbols नहीं मिले। Check करें कि सभी watchlists properly load हो रही हैं।")

    # 👇 कुकीज़ को फाइल में सेव करें
    with open("tradingview_cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("🍪 Cookies saved to tradingview_cookies.pkl")

    input("\n⏸️ Browser बंद करने के लिए Enter दबाएँ...")
    driver.quit()

if __name__ == "__main__":
    main()
