import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="GOLD 90 Day Backtest", layout="wide")
st.title("🥇 GOLD - 90 Days Backtest Result")

# 90 din ka data
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

st.write(f"Testing Period: {start_date.date()} to {end_date.date()}")

@st.cache_data
def get_gold_data():
    data = yf.download("GC=F", start=start_date, end=end_date, interval="1d")
    return data

try:
    df = get_gold_data()
    
    if df.empty:
        st.error("Data nahi aa raha, thodi der me try kar")
    else:
        # Simple logic for backtest - teri strategy ke hisab se
        df['Change'] = df['Close'].pct_change()*100
        
        st.subheader("Last 90 Days Data")
        st.dataframe(df.tail(20))

        # Sample Win/Loss logic
        green_days = len(df[df['Close'] > df['Open']])
        red_days = len(df[df['Close'] < df['Open']])
        total = len(df)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Trading Days", total)
        col2.metric("Green Days (Buy Win)", green_days)
        col3.metric("Red Days", red_days)
        
        win_rate = (green_days/total)*100 if total>0 else 0
        st.success(f"Approx Win Rate: {win_rate:.2f}%")
        
        st.line_chart(df['Close'])

except Exception as e:
    st.error(f"Error: {e}")
    st.write("yfinance add kiya hai na requirements.txt me? Check kar le.")
