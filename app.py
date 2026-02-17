import streamlit as st
import yfinance as yf
import pandas_ta as ta
import google.generativeai as genai
import pandas as pd
import time
from datetime import datetime

# --- 1. PAGE CONFIG & DESIGN ---
st.set_page_config(page_title="Jarvis AI Terminal", page_icon="🤖", layout="wide")

# Jarvis HUD Theme (Dark Blue & Cyan)
st.markdown("""
    <style>
    .main { background-color: #00050a; color: #00f2ff; }
    .stMetric { background-color: #001a2e; padding: 15px; border-radius: 10px; border: 1px solid #00f2ff; }
    .ai-box { background-color: #001f3f; padding: 20px; border-radius: 10px; border-left: 5px solid #00f2ff; color: #e0faff; font-style: italic; }
    h1, h2, h3 { color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff55; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (Persistence) ---
if 'wallet' not in st.session_state:
    st.session_state.wallet = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# --- 3. AI CONFIGURATION ---
# Streamlit Secrets se API key uthayega (Security)
apiKey = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=apiKey)
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

# --- 4. SMART DATA ENGINE ---
def get_market_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo", interval="1h")
        if df.empty: return None, None, False
        
        # Indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        
        # Whale Detection
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        is_whale = df['Volume'].iloc[-1] > (df['Vol_Avg'].iloc[-1] * 2)
        
        return df, stock.news, is_whale
    except:
        return None, None, False

def ask_jarvis(summary):
    prompt = f"Aap Jarvis hain. Is market data ka analysis karein aur professional advice dein: {summary}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Sir, server issues. AI advise unavailable."

# --- 5. UI LAYOUT ---
st.title("🖥️ JARVIS GLOBAL TERMINAL v4.0")
st.sidebar.title("System Controls")
selected_coins = st.sidebar.multiselect("Select Assets", 
                                       ["BTC-USD", "ETH-USD", "RELIANCE.NS", "SBIN.NS", "TATAMOTORS.NS"],
                                       default=["BTC-USD", "RELIANCE.NS"])

main_col, wallet_col = st.columns([2, 1])

with wallet_col:
    st.subheader("💳 Wallet Core")
    st.metric("Available Cash", f"₹{st.session_state.wallet:,.2f}")
    if st.session_state.portfolio:
        st.write("**Holdings:**")
        for t, p in st.session_state.portfolio.items():
            st.write(f"• {t} (Bought at ₹{p:.2f})")

with main_col:
    if st.button("Initialize System Scan"):
        st.info("Scanning frequencies... Please wait.")
        market_summary = ""
        
        for ticker in selected_coins:
            df, news, is_whale = get_market_data(ticker)
            if df is not None:
                curr_p = df['Close'].iloc[-1]
                curr_rsi = df['RSI'].iloc[-1]
                curr_ema = df['EMA_200'].iloc[-1]
                
                # Logic for Paper Trading
                if curr_rsi < 30 and curr_p > curr_ema:
                    if ticker not in st.session_state.portfolio:
                        st.session_state.portfolio[ticker] = curr_p
                        st.session_state.wallet -= curr_p
                        st.success(f"PAPER BUY: {ticker} @ {curr_p:.2f}")

                # Display Visuals
                whale_status = "🐳 WHALE ALERT" if is_whale else "Normal Volume"
                st.metric(label=f"{ticker} ({whale_status})", value=f"{curr_p:.2f}", delta=f"RSI: {curr_rsi:.2f}")
                market_summary += f"{ticker}: Price {curr_p}, RSI {curr_rsi}, Whale: {is_whale}. "
            else:
                st.error(f"Uplink fail: {ticker}")

        # AI Advice Section
        if market_summary:
            st.divider()
            with st.spinner("Jarvis is thinking..."):
                advice = ask_jarvis(market_summary)
                st.markdown(f"<div class='ai-box'>🤖 Jarvis: {advice}</div>", unsafe_allow_html=True)

st.caption(f"System Time: {datetime.now().strftime('%H:%M:%S')}")
