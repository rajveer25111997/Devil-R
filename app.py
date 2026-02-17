import streamlit as st
import yfinance as yf
import pandas_ta as ta
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Jarvis AI Terminal", page_icon="🤖", layout="wide")

# Custom CSS for Cyberpunk/Jarvis Look
st.markdown("""
    <style>
    .main { background-color: #00050a; color: #00f2ff; }
    .stMetric { background-color: #001a2e; padding: 15px; border-radius: 10px; border: 1px solid #00f2ff; }
    .chart-container { border: 1px solid #00f2ff55; border-radius: 10px; padding: 10px; background: #000a12; }
    h1, h2, h3 { color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff55; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

# --- 3. DATA CATEGORIES ---
crypto_assets = ["BTC-USD", "ETH-USD", "SOL-USD"]
indian_assets = ["^NSEI", "RELIANCE.NS", "SBIN.NS"]

# --- 4. DATA FETCHING FUNCTION ---
def fetch_data(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="1mo", interval="1h")
        if not df.empty:
            df['RSI'] = ta.rsi(df['Close'], length=14)
            return df
    except:
        return None
    return None

# --- 5. APP UI ---
st.title("🖥️ JARVIS GLOBAL VISUAL TERMINAL")

# Tabs for different markets
tab1, tab2 = st.tabs(["🚀 CRYPTO MARKET", "🇮🇳 NIFTY & INDIAN STOCKS"])

# --- TAB 1: CRYPTO MARKET ---
with tab1:
    st.subheader("Crypto Price Trends")
    cols = st.columns(len(crypto_assets))
    
    for i, ticker in enumerate(crypto_assets):
        df = fetch_data(ticker)
        if df is not None:
            with cols[i]:
                curr_price = df['Close'].iloc[-1]
                st.metric(ticker, f"${curr_price:,.2f}")
                # Chart display
                st.write(f"{ticker} 30-Day Trend")
                st.line_chart(df['Close'], use_container_width=True)
        else:
            st.error(f"Failed to load {ticker}")

# --- TAB 2: INDIAN MARKET ---
with tab2:
    st.subheader("Nifty 50 & Bluechip Analysis")
    cols = st.columns(len(indian_assets))
    
    for i, ticker in enumerate(indian_assets):
        df = fetch_data(ticker)
        if df is not None:
            with cols[i]:
                curr_price = df['Close'].iloc[-1]
                label = "NIFTY 50" if ticker == "^NSEI" else ticker
                st.metric(label, f"₹{curr_price:,.2f}")
                # Chart display
                st.write(f"{label} 30-Day Trend")
                st.area_chart(df['Close'], use_container_width=True)
        else:
            st.error(f"Failed to load {ticker}")

# --- 6. AI ANALYSIS SECTION ---
st.divider()
if st.button("🤖 Jarvis, Analyze Visual Patterns"):
    with st.spinner("Processing visual data and charts..."):
        # Dummy summary for AI (Expandable with logic)
        summary = "Sir, charts show consistent support for Nifty at current levels, while Crypto is in a consolidation phase."
        prompt = f"Aap Jarvis hain. Is market summary par professional advice dein: {summary}"
        try:
            response = model.generate_content(prompt)
            st.info(f"**Jarvis Advice:** {response.text}")
        except:
            st.error("AI Link Offline.")

st.caption(f"Last Terminal Sync: {datetime.now().strftime('%H:%M:%S')}")
