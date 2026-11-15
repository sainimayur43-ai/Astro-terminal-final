import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="GOLD 90 Day Backtest", layout="wide")
st.title("🥇 GOLD - 90 Days Backtest - FIXED")

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

@st.cache_data
def get_gold_data():
    data = yf.download("GC=F", start=start_date, end=end_date, interval="1d", auto_adjust=True)
    return data

try:
    df = get_gold_data()
    st.write(f"Data from {start_date.date()} to {end_date.date()}")
    
    if df.empty:
        st.error("Data nahi aa raha")
    else:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        st.dataframe(df.tail(20))
        
        green = len(df[df['Close'] > df['Open']])
        red = len(df[df['Close'] < df['Open']])
        total = len(df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Days", total)
        c2.metric("Green Days", green)
        c3.metric("Red Days", red)
        
        win_rate = (green/total*100) if total>0 else 0
        st.success(f"Buy Win: {win_rate:.2f}% | Sell Win: {(red/total*100):.2f}%")
        st.line_chart(df['Close'])

except Exception as e:
    st.error(f"Error: {e}")
