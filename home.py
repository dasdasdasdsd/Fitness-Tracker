import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def render_home(df_weight, df_nutrition, df_workout, df_muscle):
    """Renderizza la pagina Home"""

    st.header("🏠 Dashboard")

    # ============================================
    # SEZIONE PESO CON NAVIGAZIONE MESE
    # ============================================

    

    # ============================================
    # METRICHE GENERALI
    # ============================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 Rilevazioni Peso",
            value=len(df_weight) if not df_weight.empty else 0
        )

    with col2:
        st.metric(
            label="🍎 Record Nutrizione",
            value=len(df_nutrition) if not df_nutrition.empty else 0
        )

    with col3:
        st.metric(
            label="💪 Allenamenti",
            value=len(df_workout) if not df_workout.empty else 0
        )
    with col4:
        st.metric(
            label="📅 Muscoli",
            value=len(df_muscle) if not df_muscle.empty else 0
        )