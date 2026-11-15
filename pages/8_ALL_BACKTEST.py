import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="ALL TOOLS REALITY CHECK", layout="wide")
st.title("🔮 ALL TOOLS REALITY CHECK")
st.caption("Live Backtest - Har tool ka alag result")

try:
    import swisseph as swe
    HAS_SWE = True
except:
    HAS_SWE = False
    st.warning("Swiss Ephemeris install nahi hai, basic logic chal raha hai")

def get_planet_data(dt):
    if not HAS_SWE:
        return dt.hour, dt.minute, 0, 0
    try:
        ist = pytz.timezone('Asia/Kolkata')
        dt_ist = ist.localize(dt)
        dt_ut = dt_ist.astimezone(pytz.utc)
        jd = swe.julday(dt_ut.year, dt_ut.month, dt_ut.day, dt_ut.hour + dt_ut.minute/60.0)
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_rashi = int(moon / 30)
        moon_nak = int(moon / 13.3333)
        return moon_rashi, moon_nak, int(sun/30), moon
    except:
        return None, None, None, None

def check_power_time(t):
    moon_rashi, _, _, _ = get_planet_data(t)
    if moon_rashi is None: return None
    if moon_rashi in [1, 3, 7, 10]: return "BUY"
    if moon_rashi in [2, 5, 8]: return "SELL"
    return None

def check_smart_time(t):
    _, moon_nak, _, _ = get_planet_data(t)
    if moon_nak is None: return None
    if moon_nak in [8, 12, 21, 23, 26]: return "BUY"
    if moon_nak in [9, 18, 19]: return "SELL"
    return None

def check_swing_tracker(t):
    _, _, _, moon_deg = get_planet_data(t)
    if moon_deg is None: return None
    # Waxing = BUY, Waning = SELL
    sun = swe.calc_ut(swe.julday(t.year, t.month, t.day, t.hour), swe.SUN)[0][0] if HAS_SWE else 0
    moon = swe.calc_ut(swe.julday(t.year, t.month, t.day, t.hour), swe.MOON)[0][0] if HAS_SWE else 90
    diff = (moon - sun) % 360
    return "BUY" if 0 < diff < 180 else "SELL"

@st.cache_data(ttl=3600)
def get_gold_data():
    df = yf.download("GC=F", period="3mo", interval="1h")
    df.reset_index(inplace=True)
    return df

def run_backtest(check_func):
    df = get_gold_data()
    total, win = 0, 0
    for i in range(len(df)-24):
        candle_time = df.iloc[i]['Datetime'] if 'Datetime' in df.columns else df.iloc[i]['Date']
        try:
            t = pd.to_datetime(candle_time).tz_localize('UTC').tz_convert('Asia/Kolkata').to_pydatetime()
            t = t.replace(tzinfo=None)
        except:
            t = pd.to_datetime(candle_time).to_pydatetime()
        signal = check_func(t)
        if signal:
            total += 1
            entry = float(df.iloc[i]['Close'])
            future = float(df.iloc[i+4]['Close'])
            is_win = (future > entry) if signal == "BUY" else (future < entry)
            if is_win: win += 1
    pct = (win/total*100) if total>0 else 0
    return total, win, pct

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("⚡ POWER TIME")
    total, win, pct = run_backtest(check_power_time)
    st.metric("Total", total)
    st.metric("Sahi", win)
    st.metric("Win %", f"{pct:.1f}%")
with col2:
    st.subheader("🏆 SMART TIME")
    total, win, pct = run_backtest(check_smart_time)
    st.metric("Total", total)
    st.metric("Sahi", win)
    st.metric("Win %", f"{pct:.1f}%")
with col3:
    st.subheader("📈 SWING TRACKER")
    total, win, pct = run_backtest(check_swing_tracker)
    st.metric("Total", total)
    st.metric("Sahi", win)
    st.metric("Win %", f"{pct:.1f}%")
