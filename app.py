import streamlit as st
from datetime import datetime
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from notion_client import Client

from home import render_home
from weight import render_weight
from nutrition import render_nutrition
from workout import render_workout

# ============================================
# CONFIG PAGINA (solo una volta, in alto)
# ============================================
st.set_page_config(
    page_title="Dashboard Allenamento e Nutrizione",
    page_icon="📊",
    layout="wide",
)

# ============================================
# CONFIGURAZIONE GOOGLE SHEETS
# ============================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

NUTRITION_SHEET_URL = "https://docs.google.com/spreadsheets/d/1BeB5VgoyUWgtEhittnd4wtfglFZfT5ARUPTMAS39gR8/edit?gid=0#gid=0"
WEIGHT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1MpQxnKmDatxAPBqZI7GXbwsLESUifHUDAwn25Eh_KRE/edit?gid=0#gid=0"

@st.cache_resource
def get_sheets_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(credentials)

@st.cache_data(ttl=300)
def load_google_sheet(sheet_url: str) -> pd.DataFrame:
    client = get_sheets_client()
    sheet = client.open_by_url(sheet_url)
    data = sheet.sheet1.get_all_records()
    return pd.DataFrame(data)

# ============================================
# CONFIGURAZIONE NOTION
# ============================================
@st.cache_resource
def get_notion_client() -> Client:
    # Se il token è dentro gcp_service_account.notion (come nel tuo debug)
    token = st.secrets["gcp_service_account"].get("notion")
    if not token:
        # fallback se un giorno lo sposti top-level
        token = st.secrets.get("NOTION_TOKEN")
    if not token:
        st.error('Secret mancante: aggiungi "notion" in [gcp_service_account] oppure NOTION_TOKEN top-level.')
        st.stop()
    return Client(auth=token)

@st.cache_data(ttl=3600)
def get_exercise_library() -> dict:
    notion = get_notion_client()
    db_id =st.secrets["gcp_service_account"]["EXERCISE_LIB_ID"]

    results = notion.databases.query(database_id=db_id)

    library = {}
    for page in results.get("results", []):
        props = page.get("properties", {})
        ex_id = page.get("id")

        title = props.get("Exercise", {}).get("title", [])
        name = title[0]["plain_text"] if title else ""

        muscle_sel = props.get("Muscle Group", {}).get("select")
        muscle = muscle_sel.get("name") if muscle_sel else ""

        type_sel = props.get("Type", {}).get("select")
        ex_type = type_sel.get("name") if type_sel else ""

        library[ex_id] = {"name": name, "muscle_group": muscle, "type": ex_type}

    return library

@st.cache_data(ttl=300)
def get_workout_data() -> pd.DataFrame:
    notion = get_notion_client()
    library = get_exercise_library()

    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        kwargs = {"database_id": st.secrets["gcp_service_account"]["WORKOUT_DB_ID"]}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor

        response = notion.databases.query(**kwargs)
        all_results.extend(response.get("results", []))

        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    rows = []
    for page in all_results:
        props = page.get("properties", {})
        try:
            date_obj = props.get("Date", {}).get("date")
            date = date_obj.get("start") if date_obj else None

            rel = props.get("Exercise", {}).get("relation", [])
            ex_id = rel[0]["id"] if rel else None

            ex = library.get(ex_id, {})
            ex_name = ex.get("name", "")
            muscle = ex.get("muscle_group", "")
            ex_type = ex.get("type", "")

            sets_ = props.get("Sets", {}).get("number")
            reps_ = props.get("Reps", {}).get("number")
            weight_ = props.get("Weight", {}).get("number")

            rows.append(
                {
                    "Date": date,
                    "Exercise": ex_name,
                    "Muscle Group": muscle,
                    "Type": ex_type,
                    "Sets": sets_ if sets_ is not None else 0,
                    "Reps": reps_ if reps_ is not None else 0,
                    "Weight": weight_ if weight_ is not None else 0,
                }
            )
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        for col in ["Sets", "Reps", "Weight"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

# ============================================
# DEBUG sicuro (solo chiavi, non valori)
# ============================================
if "secrets_checked" not in st.session_state:
    st.write("st.secrets keys:", list(st.secrets.keys()))
    st.session_state.secrets_checked = True

# ============================================
# SIDEBAR / NAV
# ============================================
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("🔧 Menu")

if st.sidebar.button("🏠 Home", key="btn_home", use_container_width=True):
    st.session_state.page = "Home"
    st.rerun()
if st.sidebar.button("🍎 Nutrition", key="btn_nutrition", use_container_width=True):
    st.session_state.page = "Nutrition"
    st.rerun()
if st.sidebar.button("⚖️ Weight", key="btn_weight", use_container_width=True):
    st.session_state.page = "Weight"
    st.rerun()
if st.sidebar.button("💪 Workout", key="btn_workout", use_container_width=True):
    st.session_state.page = "Workout"
    st.rerun()

if st.sidebar.button("🔄 Aggiorna dati", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"**Ultimo aggiornamento:**\n{datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ============================================
# HEADER + ROUTING
# ============================================
st.title("Dashboard Allenamento e Nutrizione")
st.markdown("---")

page = st.session_state.page

if page == "Home":
    df_weight = load_google_sheet(WEIGHT_SHEET_URL)
    df_nutrition = load_google_sheet(NUTRITION_SHEET_URL)
    df_workout = get_workout_data()
    render_home(df_weight, df_nutrition, df_workout)

elif page == "Nutrition":
    df_nutrition = load_google_sheet(NUTRITION_SHEET_URL)
    render_nutrition(df_nutrition)

elif page == "Weight":
    df_weight = load_google_sheet(WEIGHT_SHEET_URL)
    render_weight(df_weight)

elif page == "Workout":
    df_workout = get_workout_data()
    render_workout(df_workout)
