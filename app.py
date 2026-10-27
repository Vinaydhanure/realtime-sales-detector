import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from detector import check_anomaly
import time

st.set_page_config(page_title="Real-Time Sales Monitor", layout="wide")
st_autorefresh(interval=10000, key="refresh")

st.title("🔴 LIVE E-Commerce Sales Monitor")

# FIXED: Now taking 5 values
is_anomaly, drop_pct, cause, last_5, prev_avg = check_anomaly()

if is_anomaly:
    st.error(f"🚨 ALERT: Sales dropped by {drop_pct}% in last 5 mins!")
    st.warning(f"🔍 ROOT CAUSE: {cause}")
else:
    st.success(f"✅ Sales Normal | Last 5 min: Rs.{int(last_5)} | Avg: Rs.{int(prev_avg)}")

# Load live data
conn = sqlite3.connect('sales.db')
try:
    df = pd.read_sql("SELECT * FROM orders ORDER BY timestamp DESC LIMIT 200", conn)
except:
    st.info("No data yet. Make sure live_generator.py is running.")
    st.stop()

df['timestamp'] = pd.to_datetime(df['timestamp'])

if df.empty:
    st.info("Waiting for live orders... Make sure live_generator.py is running in other terminal.")
    st.stop()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Live Sales Per Minute")
    per_min = df[df['payment_status']=='Success'].groupby(pd.Grouper(key='timestamp', freq='1min'))['amount'].sum().reset_index()
    fig = px.line(per_min, x='timestamp', y='amount', markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("❌ Payment Failures by City")
    fail = df[df['payment_status']=='Failed'].groupby('city').size().reset_index(name='fails')
    if not fail.empty:
        fig2 = px.bar(fail, x='city', y='fails', color='city')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("No failures in last 200 orders - Good!")

st.subheader("📦 Last 200 Live Orders (Auto-updating)")
st.dataframe(df, use_container_width=True)

st.caption(f"Last updated: {time.strftime('%H:%M:%S')} | Refreshes every 10s")