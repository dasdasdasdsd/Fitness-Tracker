import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from notion_client import Client

# ── Google Sheets ──────────────────────────────────────────────
@st.cache_resource
def get_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def get_sheet_data(sheet_name):
    client = get_sheets_client()
    sheet = client.open(st.secrets["SHEET_NAME"]).worksheet(sheet_name)
    return pd.DataFrame(sheet.get_all_records())

# ── Notion ─────────────────────────────────────────────────────
@st.cache_resource
def get_notion_client():
    return Client(auth=st.secrets["NOTION_TOKEN"])

@st.cache_data(ttl=3600)
def get_exercise_library():
    notion = get_notion_client()
    results = notion.databases.query(database_id=st.secrets["EXERCISE_LIB_ID"])
    library = {}
    for page in results["results"]:
        props = page["properties"]
        ex_id = page["id"]
        name = props["Exercise"]["title"][0]["text"]["content"] if props["Exercise"]["title"] else ""
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
            date   = props["Date"]["date"]["start"] if props["Date"]["date"] else None
            ex_id  = props["Exercise"]["relation"][0]["id"] if props["Exercise"]["relation"] else None
            ex_name = library[ex_id]["name"] if ex_id and ex_id in library else ""
            muscle  = library[ex_id]["muscle_group"] if ex_id and ex_id in library else ""
            ex_type = library[ex_id]["type"] if ex_id and ex_id in library else ""
            sets   = props["Sets"]["number"]
            reps   = props["Reps"]["number"]
            weight = props["Weight"]["number"]
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

# ── Sidebar ────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("🏋️ Fitness Tracker")

if st.sidebar.button("🏠 Home",      use_container_width=True): st.session_state.page = "Home";      st.rerun()
if st.sidebar.button("⚖️ Weight",    use_container_width=True): st.session_state.page = "Weight";    st.rerun()
if st.sidebar.button("💪 Workout",   use_container_width=True): st.session_state.page = "Workout";   st.rerun()

if st.sidebar.button("🔄 Refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

page = st.session_state.page

# ── Routing ────────────────────────────────────────────────────
if page == "Home":
    from home import render_home
    render_home()

elif page == "Weight":
    from weight import render_weight
    df_weight = get_sheet_data("Weight")  #← Google Sheets
    render_weight(df_weight)

elif page == "Workout":
    from workout import render_workout
    df_workout = get_workout_data()       # ← Notion
    render_workout(df_workout)
