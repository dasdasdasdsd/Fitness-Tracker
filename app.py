import streamlit as st
from datetime import datetime
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from home import render_home
from weight import render_weight
from nutrition import render_nutrition
from workout import render_workout

# ============================================
# CONFIGURAZIONE GOOGLE SHEETS
# ============================================

# Scope per accedere a Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# URL dei Google Sheets
Nutrition_sheet = "https://docs.google.com/spreadsheets/d/1BeB5VgoyUWgtEhittnd4wtfglFZfT5ARUPTMAS39gR8/edit?gid=0#gid=0"
Weight_sheet = "https://docs.google.com/spreadsheets/d/1MpQxnKmDatxAPBqZI7GXbwsLESUifHUDAwn25Eh_KRE/edit?gid=0#gid=0"
Workout_sheet = "https://docs.google.com/spreadsheets/d/1APCir1V_w2xzZEvTmTbl8eBDj0eloH33RF2LrQRJTZ8/edit?gid=0#gid=0"

@st.cache_resource
def get_google_sheets_client():
    """Connessione a Google Sheets usando service account"""
    try:
        credentials = Credentials.from_service_account_file(
            'concise-upgrade-428317-d7-7b2192f7f944.json',
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Errore connessione Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)  # Cache per 5 minuti
def load_google_sheet(sheet_url, worksheet_name=None):
    """Carica dati da Google Sheet"""
    try:
        client = get_google_sheets_client()
        if client is None:
            return pd.DataFrame()

        sheet = client.open_by_url(sheet_url)

        if worksheet_name:
            worksheet = sheet.worksheet(worksheet_name)
        else:
            worksheet = sheet.sheet1

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        return df
    except Exception as e:
        st.error(f"Errore caricamento sheet: {e}")
        return pd.DataFrame()

# ============================================
# CONFIGURAZIONE PAGINA
# ============================================

st.set_page_config(
    page_title="Dashboard Allenamento e Nutrizione",
    page_icon="📊",
    layout="wide"
)

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("🔧 Menu")
page = st.sidebar.selectbox(
    "Seleziona sezione",
    ["Home", "Nutrition", "Weight", "Workout"]
)

# Pulsante refresh
if st.sidebar.button("🔄 Aggiorna dati"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"**Ultimo aggiornamento:**\n{datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ============================================
# HEADER
# ============================================

st.title("Dashboard Allenamento e Nutrizione")
st.markdown("---")

# ============================================
# CARICA DATI E ROUTING
# ============================================

# Carica i dati
df_weight = load_google_sheet(Weight_sheet)
df_nutrition = load_google_sheet(Nutrition_sheet)
df_workout = load_google_sheet(Workout_sheet)

# Routing pagine
if page == "Home":
    render_home(df_weight, df_nutrition, df_workout)
elif page == "Nutrition":
    render_nutrition(df_nutrition)
elif page == "Weight":
    render_weight(df_weight)
elif page == "Workout":
    render_workout(df_workout)
