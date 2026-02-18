import streamlit as st
import pandas as pd
import plotly.express as px

def render_workout(df):
    st.header("💪 Workout")
    
    if df.empty:
        st.warning("⚠️ No data")
        return
    
    # FIX: Pulisci + numeric FORZATO
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    num_cols = ['Sets', 'Reps', 'Weight']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if df.empty:
        st.error("❌ Colonne mancanti: Date/Sets/Reps/Weight")
        return
    
    # 📊 Metriche
    st.subheader("📊 Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessioni", df['Date'].nunique())
    col2.metric("Esercizi unici", df['Exercise'].nunique() if 'Exercise' in df else 0)
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight']
    col3.metric("Volume tot", f"{df['Volume'].sum():,.0f}")
    col4.metric("Giorni", len(df['Date'].dt.date.unique()))
    
        # Dopo metriche in workout.py
    st.subheader("📅 Heatmap stile GitHub")
    df['Weight_num'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight_num']
    daily_volume = df.groupby(df['Date'].dt.date)['Volume'].sum().reset_index()
    daily_volume.columns = ['date', 'value']
    daily_volume['date'] = pd.to_datetime(daily_volume['date'])
    # daily_volume già calcolato (da prima)
    st.subheader("📅 Heatmap GitHub-style")
    import lesley
    fig = lesley.cal_heatmap(
        daily_volume['date'].tolist(),
        daily_volume['value'].tolist(),
        linewidth=0.5,
        cmap="Greens"
    )
    st.pyplot(fig)

    
    # 📈 Top Esercizi (bonus)
    if 'Exercise' in df.columns:
        top_vol = df.groupby('Exercise')['Volume'].sum().sort_values(ascending=False).head(10)
        fig2 = px.bar(x=top_vol.values, y=top_vol.index, orientation='h')
        st.plotly_chart(fig2, use_container_width=True)
    
    # 🔍 Tabella
    st.dataframe(df, use_container_width=True)
