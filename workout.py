import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render_workout(df):
    st.header("💪 Workout")

    if df.empty:
        st.warning("⚠️ Nessun dato disponibile")
        return

    df = df.copy()

    # ── 1. Parse date ──────────────────────────────────────────────
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])

    # ── 2. Converti numerici ───────────────────────────────────────
    for col in ['Sets', 'Reps', 'Weight']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # ── 3. Volume ──────────────────────────────────────────────────
    df['Volume'] = df['Sets'] * df['Reps'] * df['Weight']

    # ── 4. Metriche ────────────────────────────────────────────────
    st.subheader("📊 Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessioni", df['Date'].dt.date.nunique())
    col2.metric("Esercizi unici", df['Exercise'].nunique() if 'Exercise' in df.columns else 0)
    col3.metric("Volume totale", f"{df['Volume'].sum():,.0f}")
    col4.metric("Giorni loggati", df['Date'].dt.date.nunique())

    st.markdown("---")

    # ── 5. Heatmap GitHub-style ────────────────────────────────────
    st.subheader("📅 Heatmap Allenamenti")

    daily_vol = df.groupby(df['Date'].dt.normalize())['Volume'].sum()

    year = df['Date'].dt.year.max()
    dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq='D')
    values = np.zeros(len(dates))

    for ts, vol in daily_vol.items():
        if dates[0] <= ts <= dates[-1]:
            idx = (ts - dates[0]).days
            values[idx] = vol

    # Griglia 7 x 53
    days_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    grid = np.full((7, 53), np.nan)
    text = [[""] * 53 for _ in range(7)]

    for i, (date, val) in enumerate(zip(dates, values)):
        col_idx = i // 7
        day_idx = date.weekday()
        grid[day_idx][col_idx] = val
        text[day_idx][col_idx] = f"{date.strftime('%d %b')}: {int(val)} vol"

    fig = go.Figure(go.Heatmap(
        z=grid,
        text=text,
        hovertemplate="%{text}<extra></extra>",
        colorscale="Greens",
        showscale=False,
        xgap=3,
        ygap=3,
    ))

    fig.update_layout(
        height=180,
        margin=dict(l=40, r=10, t=10, b=30),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=days_labels,
            autorange='reversed'
        ),
        xaxis=dict(showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── 6. Top Esercizi per Volume ─────────────────────────────────
    if 'Exercise' in df.columns:
        st.subheader("🏆 Top Esercizi (Volume)")
        top_vol = (
            df.groupby('Exercise')['Volume']
            .sum()
            .sort_values(ascending=True)
            .tail(10)
        )
        fig2 = px.bar(
            x=top_vol.values,
            y=top_vol.index,
            orientation='h',
            labels={'x': 'Volume (kg×reps×sets)', 'y': ''},
            color=top_vol.values,
            color_continuous_scale='Greens',
        )
        fig2.update_layout(
            height=350,
            showlegend=False,
            coloraxis_showscale=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── 7. Tabella dati ────────────────────────────────────────────
    st.subheader("🔍 Dati Allenamenti")
    st.dataframe(df.drop(columns=['Volume']), use_container_width=True, height=400)

    # ── 8. Download ────────────────────────────────────────────────
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica CSV",
        data=csv,
        file_name=f"workout_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
