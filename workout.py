import streamlit as st
from datetime import datetime
import pandas as pd
import plotly_calplot as cp

def render_workout(df):
    """Renderizza la pagina Workout"""

    st.header("Workout")

    with st.spinner("Caricamento dati..."):
        pass  # Dati già caricati da app.py
    df = pd.DataFrame({
        'Date': ['16/02/26', '16/02/26', '16/02/26', '16/02/26', '17/02/26', '17/02/26', '17/02/26', '17/02/26'],
        'Exercise': ['panca', 'dips', 'skull crusher', 'pull down', 'leg raise', 'crunch', 'military press', 'face pull raises'],
        'Sets': [3,4,3,4,4,3,3,3],
        'Reps': [8,10,10,10,15,10,10,8],
        'Weight': [36,0,0,18,0,30,32,21]  # bw=0
    })

    # Parse date
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')

    # Calcola volume giornaliero
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight'].fillna(0)
    daily_volume = df.groupby('Date')['Volume'].sum().reset_index()
    daily_volume.columns = ['date', 'value']

    # Heatmap stile GitHub (ultimi 365 giorni, 0 per giorni vuoti)
    st.subheader("📅 Heatmap Allenamenti (Volume giornaliero)")
    fig = cp.calplot(
        daily_volume,
        x="date",
        y="value",
        dark_theme=False,  # True per dark mode
        year_title=True,
        colorscale="Greens",  # Verdi GitHub
        gap=5,
        name="Volume (kg*reps*sets)"
    )
    st.plotly_chart(fig, use_container_width=True)    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Nessun dato disponibile")
