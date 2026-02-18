import streamlit as st
import pandas as pd
import numpy as np
import lesley

def render_workout(df):
    st.header("💪 Workout")
    
    if df.empty:
        st.warning("⚠️ Nessun dato")
        return

    df = df.copy()

    # 1. Fix date
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])

    # 2. Fix numerici
    for col in ['Sets', 'Reps', 'Weight']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. Volume
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight']

    # 4. Daily volume come Series indicizzata per Timestamp
    daily_vol = df.groupby(df['Date'].dt.normalize())['Volume'].sum()

    # 5. Grid anno completo
    year = df['Date'].dt.year.max()
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq='D')
    values = np.zeros(len(dates))

    for ts, vol in daily_vol.items():
        if dates[0] <= ts <= dates[-1]:
            idx = (ts - dates[0]).days
            values[idx] = vol

    # 6. Lesley → Altair → st.altair_chart (NON st.pyplot!)
    st.subheader("📅 Heatmap Allenamenti")
    chart = lesley.cal_heatmap(dates, values)
    st.altair_chart(chart, use_container_width=True)
