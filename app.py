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
# CONFIGURAZIONE GOOGLE SHEETS
# ============================================

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

Nutrition_sheet = "https://docs.google.com/spreadsheets/d/1BeB5VgoyUWgtEhittnd4wtfglFZfT5ARUPTMAS39gR8/edit?gid=0#gid=0"
Weight_sheet    = "https://docs.google.com/spreadsheets/d/1MpQxnKmDatxAPBqZI7GXbwsLESUifHUDAwn25Eh_KRE/edit?gid=0#gid=0"

@st.cache_resource
def get_sheets_client():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Errore connessione Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)
def load_google_sheet(sheet_url):
    try:
        client = get_sheets_client()
        if client is None:
            return pd.DataFrame()
        sheet = client.open_by_url(sheet_url)
        data = sheet.sheet1.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Errore caricamento sheet: {e}")
        return pd.DataFrame()


# ============================================
# CONFIGURAZIONE NOTION
# ============================================
if 'secrets_checked' not in st.session_state:
    st.write("st.secrets:",st.secrets)
    st.session_state.secrets_checked = True
@st.cache_resource
def get_notion_client():
    return Client(auth=st.secrets.gcp_service_account.notion)

@st.cache_data(ttl=3600)
def get_exercise_library():
    from notion_client import Client
    notion = Client(auth=st.secrets.gcp_service_account.notion)  # ✅
    results = notion.databases.query(
        database_id=st.secrets["EXERCISE_LIB_ID"]
    )
    return results

    library = {}
    for page in results["results"]:
        props = page["properties"]
        ex_id = page["id"]
        name   = props["Exercise"]["title"][0]["text"]["content"] if props["Exercise"]["title"] else ""
        muscle = props["Muscle Group"]["select"]["name"] if props["Muscle Group"]["select"] else ""
        ex_type = props["Type"]["select"]["name"] if props["Type"]["select"] else ""
        library[ex_id] = {"name": name, "muscle_group": muscle, "type": ex_type}
    return library

@st.cache_data(ttl=300)
def get_workout_data():
    notion = get_notion_client()
    library = get_exercise_library()

    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        kwargs = {"database_id": st.secrets["WORKOUT_DB_ID"]}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor
        response = notion.databases.query(**kwargs)
        all_results.extend(response["results"])
        has_more = response["has_more"]
        start_cursor = response.get("next_cursor")

    rows = []
    for page in all_results:
        props = page["properties"]
        try:
            date    = props["Date"]["date"]["start"] if props["Date"]["date"] else None
            ex_id   = props["Exercise"]["relation"][0]["id"] if props["Exercise"]["relation"] else None
            ex_name = library[ex_id]["name"] if ex_id and ex_id in library else ""
            muscle  = library[ex_id]["muscle_group"] if ex_id and ex_id in library else ""
            ex_type = library[ex_id]["type"] if ex_id and ex_id in library else ""
            sets    = props["Sets"]["number"]
            reps    = props["Reps"]["number"]
            weight  = props["Weight"]["number"]
            rows.append({
                "Date": date, "Exercise": ex_name,
                "Muscle Group": muscle, "Type": ex_type,
                "Sets": sets, "Reps": reps, "Weight": weight,
            })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        for col in ["Sets", "Reps", "Weight"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


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

if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("🔧 Menu")

if st.sidebar.button("🏠 Home",      key="btn_home",      use_container_width=True):
    st.session_state.page = "Home";      st.rerun()
if st.sidebar.button("🍎 Nutrition", key="btn_nutrition", use_container_width=True):
    st.session_state.page = "Nutrition"; st.rerun()
if st.sidebar.button("⚖️ Weight",    key="btn_weight",    use_container_width=True):
    st.session_state.page = "Weight";    st.rerun()
if st.sidebar.button("💪 Workout",   key="btn_workout",   use_container_width=True):
    st.session_state.page = "Workout";   st.rerun()

if st.sidebar.button("🔄 Aggiorna dati", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"**Ultimo aggiornamento:**\n{datetime.now().strftime('%d/%m/%Y %H:%M')}")

page = st.session_state.page


# ============================================
# HEADER
# ============================================

st.title("Dashboard Allenamento e Nutrizione")
st.markdown("---")


# ============================================
# CARICA DATI E ROUTING
# ============================================

if page == "Home":
    df_weight    = load_google_sheet(Weight_sheet)
    df_nutrition = load_google_sheet(Nutrition_sheet)
    df_workout   = get_workout_data()
    render_home(df_weight, df_nutrition, df_workout)

elif page == "Nutrition":
    df_nutrition = load_google_sheet(Nutrition_sheet)
    render_nutrition(df_nutrition)

elif page == "Weight":
    df_weight = load_google_sheet(Weight_sheet)
    render_weight(df_weight)

elif page == "Workout":
    df_workout = get_workout_data()
    render_workout(df_workout)
