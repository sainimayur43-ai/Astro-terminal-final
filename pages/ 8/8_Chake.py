import streamlit as st
import pandas as pd
import yfinance as yf
import pytz
from datetime import datetime

st.set_page_config(page_title="CHAKE PAY CHECK", layout="wide")
st.title("🔥 CHAKE PAY - REALITY CHECK")
st.caption(f"LIVE 90 Days Backtest - {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%b %I:%M %p')}")

def safe_dt(x):
    try:
        s = pd.to_datetime(x, utc=True, errors='coerce')
        return s.dt.tz_convert('Asia/Kolkata')
    except:
        return pd.to_datetime(x, errors='coerce', utc=True)

@st.cache_data(ttl=600)
def get_data(symbol):
    df = yf.download(symbol, period="3mo", interval="15m", progress=False, auto_adjust=True)
    df.reset_index(inplace=True)
    col = 'Datetime' if 'Datetime' in df.columns else 'Date'
    df['Datetime'] = safe_dt(df[col])
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

gold_df = get_data("GC=F")
nifty_df = get_data("^NSEI")

st.info("👇 Chake Pay ke jo time hote hain (roz alag), unka fixed time kya hai? Jaise MOST POWERFUL ke 07:42, 14:15 the, waise Chake Pay ke kya hain?")

# User se Chake Pay ke times lo
c1, c2, c3 = st.columns(3)
with c1:
    cp1 = st.text_input("Chake Pay Time 1", "10:15")
with c2:
    cp2 = st.text_input("Chake Pay Time 2", "13:30")
with c3:
    cp3 = st.text_input("Chake Pay Time 3", "15:00")

def parse_times(t_list):
    parsed=[]
    for t in t_list:
        try:
            h,m = map(int, t.split(':'))
            parsed.append((h,m))
        except: pass
    return parsed

def check_chake_pay(df, times):
    total=wins=0
    results=[]
    for i in range(len(df)-5):
        dt=df.iloc[i]['Datetime']
        for h,m in times:
            if dt.hour==h and abs(dt.minute-m)<=10:
                total+=1
                entry=df.iloc[i]['Close']
                future_max=df.iloc[i+1:i+5]['High'].max()
                future_min=df.iloc[i+1:i+5]['Low'].min()
                up = ((future_max-entry)/entry)*100
                win = up > 0.05
                if win: wins+=1
                results.append({"Date": dt.strftime("%d-%b"), "Time": f"{h:02d}:{m:02d}", "Price": round(entry,2), "Up%": round(up,3), "Result": "✅ WIN" if win else "❌ LOSS"})
    pct=round(wins/total*100,1) if total else 0
    return total,wins,pct, pd.DataFrame(results)

times = parse_times([cp1, cp2, cp3])

if st.button("🔍 CHAKE PAY KA WIN% NIKALO"):
    if not times:
        st.error("Time sahi format me daalo - jaise 10:15")
    else:
        g_total,g_wins,g_pct,g_df = check_chake_pay(gold_df, times)
        n_total,n_wins,n_pct,n_df = check_chake_pay(nifty_df, times)

        st.subheader(f"🔮 CHAKE PAY ({', '.join([cp1,cp2,cp3])}) Ka 90 Din Ka Sach")

        c1,c2 = st.columns(2)
        with c1:
            st.metric("🪙 GOLD - CHAKE PAY WIN%", f"{g_pct}%", f"{g_wins}/{g_total}")
            st.progress(int(g_pct))
            if g_pct>=68:
                st.success(f"✅ CHAKE PAY GOLD me kaam kar raha hai! {g_pct}%")
            else:
                st.warning(f"⚠️ CHAKE PAY ka {g_pct}% hai")
            if not g_df.empty:
                st.dataframe(g_df.tail(20).sort_values("Date", ascending=False), use_container_width=True)
        
        with c2:
            st.metric("📈 Nifty - CHAKE PAY WIN%", f"{n_pct}%", f"{n_wins}/{n_total}")
            st.progress(int(n_pct))
            if not n_df.empty:
                st.dataframe(n_df.tail(20).sort_values("Date", ascending=False), use_container_width=True)

st.divider()
st.write("LIVE Gold")
st.dataframe(gold_df.tail(3)[['Datetime','Close']])

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
