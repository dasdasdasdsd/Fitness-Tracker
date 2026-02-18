import streamlit as st
from datetime import datetime
import pandas as pd
import plotly_calplot as cp

def render_workout(df):
    """Renderizza la pagina Workout"""

    st.header("Workout")

    with st.spinner("Caricamento dati..."):
        pass  # Dati già caricati da app.py

    # Parse robusto (funziona su Sheets)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])  # Rimuovi invalidi


    # Calcola volume giornaliero
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight'].fillna(0)
    daily_volume = df.groupby('Date')['Volume'].sum().reset_index()
    daily_volume.columns = ['date', 'value']

    # Heatmap (dopo metriche)
    st.subheader("📅 Heatmap Allenamenti")
    if 'Date' in df.columns and not df['Date'].empty:
        # Calcola volume (bw=0)
        df['Weight_num'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
        df['Volume'] = df['Sets'] * df['Reps'] * df['Weight_num']
        
        daily_volume = df.groupby(df['Date'].dt.date)['Volume'].sum().reset_index()
        daily_volume.columns = ['date', 'value']
        daily_volume['date'] = pd.to_datetime(daily_volume['date'])
        
        fig = cp.calplot(
            daily_volume, x="date", y="value",
            dark_theme=st.get_option("theme.base") == "dark",
            colorscale="Greens",
            year_title=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📅 Aggiungi colonne Date/Sets/Reps/Weight")

