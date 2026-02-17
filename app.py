# --- PROJECT JARVIS: FINAL WEB EDITION ---
# Is file ko 'app.py' naam se save karein

import yfinance as yf
import ccxt
import pandas_ta as ta
import time
import threading
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request

# 1. SETUP & CONFIGURATION
app = Flask(__name__)

# --- AI Setup ---
# Apni API Key yahan dalein
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

# --- Global Variables (Bot ki Memory) ---
st.session_state.wallet = 100000
portfolio = {}
market_status = {} # Website par dikhane ke liye
coins = ["BTC-USD", "ETH-USD", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"]
danger_words = ["crash", "scam", "hack", "ban", "drop", "stolen"]

# 2. JARVIS LOGIC FUNCTIONS
def ask_jarvis(data_summary):
    """AI se trading advice mangne wala function"""
    try:
        prompt = f"Aap Jarvis hain. Is data ko dekh kar short trading advice dein: {data_summary}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Sir, AI connectivity mein dikkat hai. Math logic check karein."

def get_market_data_smart(ticker):
    # matlab: ye function pehale yohoo se koshish karega
    try:
       stock = yf.Ticker(ticker)
       df = stock.history(period="1mo", interval="1h")
       if not df.empty:
          #ager data mil gaya toh dataframe aur "yahoo" naam bhej do
          return df, stock, "Yahoo"
    except:
        pass # ager yahoo fail hua, toh niche jayega

    # yahan humnw backup rakha hai (Abhi ke leye none)
    return None, None, "Fail"

def run_trading_bot():
    """Ye bot background mein hamesha chalta rahega"""
    global wallet, market_status, portfolio

    print("🤖 Jarvis: Market Scanning Shuru kar raha hoon...")

    while True:
        for ticker in coins:
            try:
                # A. Data Fetching
                df, data, source = get_market_data_smart(ticker)

                # B. Indicators
                if df is not None:
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    df['EMA_200'] = ta.ema(df['Close'], length=200)
                    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
                else:
                    print(f"{ticker} ka data kahin se nahi mila. Skipping...")
            except Exception as e:
                print(f"Error in {ticker}: {e}")

                curr_price = df['Close'].iloc[-1]
                curr_rsi = df['RSI'].iloc[-1]
                curr_ema = df['EMA_200'].iloc[-1]
                curr_vol = df['Volume'].iloc[-1]
                avg_vol = df['Vol_Avg'].iloc[-1]

                # C. News & Whale Detection
                news = data.news
                headline = news[0].get('title', 'No News') if news else "No News Found"

                whale_alert = "Normal"
                if curr_vol > (avg_vol * 2):
                    whale_alert = "⚠️ WHALE ENTRY DETECTED"

                is_bad_news = any(word in headline.lower() for word in danger_words)

                # D. AI Advice (Sirf Setup par)
                ai_msg = "Sukun se baithiye, koi setup nahi hai."
                if curr_rsi < 35 or curr_rsi > 65:
                    summary = f"Stock: {ticker}, Price: {curr_price}, RSI: {curr_rsi}, News: {headline}"
                    ai_msg = ask_jarvis(summary)

                # E. Paper Trading Logic
                trade_action = "Wait"
                if curr_rsi < 30 and curr_price > curr_ema and not is_bad_news:
                    if ticker not in portfolio:
                        portfolio[ticker] = curr_price
                        wallet -= curr_price
                        trade_action = "BUY"

                elif curr_rsi > 70 and ticker in portfolio:
                    buy_p = portfolio.pop(ticker)
                    wallet += curr_price
                    trade_action = f"SELL (Profit: {curr_price - buy_p:.2f})"

                # F. Update Website Data
                market_status[ticker] = {
                    "price": round(curr_price, 2),
                    "rsi": round(curr_rsi, 2),
                    "whale": whale_alert,
                    "news": headline,
                    "ai_advice": ai_msg,
                    "action": trade_action
                }

                print(f"✅ Updated: {ticker} | Price: {curr_price:.2f}")

            except Exception as e:
                 print(f"❌ Error in {ticker}: {e}")

        time.sleep(60) # 5 Minute Break

# 3. WEB ROUTES
@app.route('/')
def home():
    # Asali website ke liye hum 'templates/index.html' use karenge
    return "Jarvis Dashboard is Running! Go to /api/status"

@app.route('/api/status')
def get_status():
    return jsonify({
        "market": market_status,
        "wallet": round(wallet, 2),
        "holdings": list(portfolio.keys())
    })

# 4. START SYSTEM
if __name__ == '__main__':
    # Bot ko alag thread mein shuru karein
    bot_thread = threading.Thread(target=run_trading_bot, daemon=True)
    bot_thread.start()

    # Web server shuru karein
    st.rerun(debug=True, port=5000)
