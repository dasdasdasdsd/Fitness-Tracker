import streamlit as st
from datetime import datetime

def render_workout(df):
    """Renderizza la pagina Workout"""

    st.header("Workout")

    with st.spinner("Caricamento dati..."):
        pass  # Dati già caricati da app.py

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Nessun dato disponibile")
