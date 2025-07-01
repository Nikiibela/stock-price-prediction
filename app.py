import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import ta
import warnings
from datetime import date

# Optional: suppress warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="📈 Stock Predictor App", layout="wide")
st.title("📊 Stock Predictor - by Nikita Bela")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g., AAPL)", value="AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime(date.today()))

# Download data
if ticker:
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    if not df.empty:
        st.subheader(f"📄 Last 5 Rows of {ticker}")
        st.dataframe(df.tail())

        # Technical indicators
        df['Daily Return'] = df['Close'].pct_change() * 100
        df['MA7'] = df['Close'].rolling(7).mean()
        df['MA30'] = df['Close'].rolling(30).mean()

        # RSI
        rsi_indicator = ta.momentum.RSIIndicator(close=df['Close'])
        df['RSI'] = pd.Series(rsi_indicator.rsi().values.ravel(), index=df.index)

        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = pd.Series(macd.macd().values.ravel(), index=df.index)
        df['MACD Signal'] = pd.Series(macd.macd_signal().values.ravel(), index=df.index)

        # Drop NaNs
        df.dropna(inplace=True)

        # Price chart with MA7 and MA30
        st.subheader("📈 Price Chart with MA7 & MA30")
        fig_price, ax = plt.subplots()
        ax.plot(df['Close'], label='Close Price')
        ax.plot(df['MA7'], label='MA7')
        ax.plot(df['MA30'], label='MA30')
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig_price)

        # RSI chart
        st.subheader("📉 RSI (Relative Strength Index)")
        fig_rsi, ax_rsi = plt.subplots()
        ax_rsi.plot(df['RSI'], color='purple')
        ax_rsi.axhline(70, color='red', linestyle='--')
        ax_rsi.axhline(30, color='green', linestyle='--')
        ax_rsi.set_ylabel("RSI")
        st.pyplot(fig_rsi)

        # MACD chart
        st.subheader("📊 MACD (Moving Average Convergence Divergence)")
        fig_macd, ax_macd = plt.subplots()
        ax_macd.plot(df['MACD'], label='MACD', color='blue')
        ax_macd.plot(df['MACD Signal'], label='Signal Line', color='orange')
        ax_macd.legend()
        st.pyplot(fig_macd)

        # Volume chart
        st.subheader("🔊 Volume Over Time")
        st.line_chart(df['Volume'])

        # Biggest price spike
        if df['Daily Return'].dropna().empty:
            st.warning("Not enough data to compute daily return.")
        else:
            spike_day = df['Daily Return'].abs().idxmax()
            spike_value = df.loc[spike_day]['Daily Return']
            st.success(f"⚡ Largest price change: {round(spike_value, 2)}% on {spike_day.date()}")

    else:
        st.warning("⚠️ No data found. Please check the ticker symbol and date range.")
