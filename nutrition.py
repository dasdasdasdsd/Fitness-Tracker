import streamlit as st
from datetime import datetime

def render_nutrition(df):
    """Renderizza la pagina Nutrition"""

    st.header("Nutrition")

    with st.spinner("Caricamento dati..."):
        pass  # Dati già caricati da app.py

    if not df.empty:
        # Statistiche
        st.subheader("📊 Statistiche")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Righe", len(df))
        with col2:
            st.metric("Colonne", len(df.columns))
        with col3:
            st.metric("Celle", len(df) * len(df.columns))

        st.markdown("---")

        # Filtri
        st.subheader("⚙️ Filtri")
        if len(df.columns) > 0:
            col_filter = st.selectbox("Filtra per colonna", ["Tutti"] + list(df.columns))

            if col_filter != "Tutti":
                unique_values = df[col_filter].unique()
                selected_value = st.multiselect(
                    f"Seleziona valori per {col_filter}",
                    options=unique_values
                )
                if selected_value:
                    df = df[df[col_filter].isin(selected_value)]

        # Mostra dati
        st.subheader("🔍 Dati")
        st.dataframe(df, use_container_width=True)

        # Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica CSV",
            data=csv,
            file_name=f"nutrition_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Nessun dato disponibile")
