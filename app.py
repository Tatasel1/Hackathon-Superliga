import streamlit as st
import pandas as pd
from google import genai

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="SQLScout",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STILURI CSS (TEMĂ PORTOCALIE & DESIGN FLASH) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        .stApp {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        div[data-testid="stMarkdownContainer"] p.centered-title,
        .centered-title {
            text-align: center !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            font-size: 5rem !important;
            line-height: 1.05 !important;
            letter-spacing: -0.03em !important;
            margin-bottom: 20px !important;
            color: #ff6600 !important;
            text-shadow: 0 0 40px rgba(255, 102, 0, 0.35);
        }

        h2, h3 {
            color: #ff6600 !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        div[data-testid="stButton"] {
            margin-bottom: 6px;
        }
        div[data-testid="stButton"]:last-child {
            margin-bottom: 0;
        }

        .stButton>button {
            background-color: #ff6600;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            width: 100%;
            transition: background-color 0.15s ease;
        }
        .stButton>button:hover {
            background-color: #e55c00;
            color: white;
        }

        .st-key-league_buttons {
            display: flex;
            flex-direction: row;
            gap: 12px;
        }
        .st-key-league_buttons > div {
            flex: 1;
        }
        .st-key-league_buttons div[data-testid="stButton"] {
            margin-bottom: 0;
        }

        .table-scroll-wrapper {
            width: 100%;
            overflow-x: auto;
        }

        .st-key-stats_buttons .stButton>button {
            background-color: transparent;
            color: #c7cbd3;
            border: none;
            border-left: 3px solid #2a2d34;
            border-radius: 0;
            text-align: left;
            font-weight: 500;
            padding: 10px 14px;
        }
        .st-key-stats_buttons .stButton>button:hover {
            background-color: rgba(255, 102, 0, 0.08);
            border-left: 3px solid #ff6600;
            color: #ffffff;
        }

        .compact-table {
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
        }
        .compact-table th, .compact-table td {
            white-space: nowrap;
        }
        .compact-table th {
            background-color: #1a1c21;
            color: #ff6600;
            text-align: left;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 5px 8px;
            border-bottom: 2px solid #ff6600;
        }
        .compact-table td {
            padding: 4px 8px;
            color: #e0e0e0;
            border-bottom: 1px solid #22252b;
        }
        .compact-table tr:hover td {
            background-color: #191b1f;
        }

        .match-card {
            background-color: #1e1e1e;
            border-left: 4px solid #ff6600;
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .match-teams {
            font-size: 15px;
            font-weight: 600;
            color: #e0e0e0;
        }
        .match-score {
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 600;
            color: #ff6600;
            background-color: #2a2a2a;
            padding: 3px 12px;
            border-radius: 5px;
        }
        .match-date {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            letter-spacing: 0.03em;
            color: #888888;
        }

        .league-col-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            color: #ffffff;
            border-bottom: 2px solid #ff6600;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER CENTRAT ---
st.markdown('<p class="centered-title">SQLScout</p>', unsafe_allow_html=True)
st.divider()

# --- ÎNCĂRCARE DATE ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("ROU.xlsx")
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d.%m.%Y")
        return df
    except Exception as e:
        return None

df = load_data()

# --- DATE MOCKUP PENTRU CELELALTE 3 LIGI ---
MOCK_LEAGUES = {
    "Liga 2": [
        {"Home": "Csikszereda", "Away": "Metaloglobus", "HG": 1, "AG": 0, "Date": "21.07.2026"},
        {"Home": "Unirea Slobozia", "Away": "Politehnica Iași", "HG": 2, "AG": 2, "Date": "20.07.2026"},
        {"Home": "Concordia Chiajna", "Away": "Steaua București", "HG": 0, "AG": 1, "Date": "19.07.2026"},
        {"Home": "CS Tunari", "Away": "Callatis Mangalia", "HG": 3, "AG": 1, "Date": "18.07.2026"},
    ],
    "Cupa României": [
        {"Home": "FCSB", "Away": "Petrolul Ploiești", "HG": 2, "AG": 0, "Date": "17.07.2026"},
        {"Home": "CFR Cluj", "Away": "UTA Arad", "HG": 1, "AG": 1, "Date": "16.07.2026"},
        {"Home": "Rapid", "Away": "Farul Constanța", "HG": 3, "AG": 2, "Date": "15.07.2026"},
        {"Home": "U Craiova", "Away": "Dinamo", "HG": 0, "AG": 0, "Date": "14.07.2026"},
    ],
    "Internațional": [
        {"Home": "Real Madrid", "Away": "Manchester City", "HG": 2, "AG": 1, "Date": "13.07.2026"},
        {"Home": "Bayern München", "Away": "Inter Milano", "HG": 1, "AG": 1, "Date": "12.07.2026"},
        {"Home": "PSG", "Away": "Liverpool", "HG": 0, "AG": 2, "Date": "11.07.2026"},
        {"Home": "Arsenal", "Away": "AC Milan", "HG": 3, "AG": 0, "Date": "10.07.2026"},
    ],
}

# --- AFIȘARE RECENTE (SUS DE TOT, 4 LIGI, CÂTE 4 MECIURI FIECARE) ---
league_cols = st.columns(4)

with league_cols[0]:
    st.markdown('<div class="league-col-title">Superliga</div>', unsafe_allow_html=True)
    if df is not None:
        recent_matches = df.tail(4).iloc[::-1]
        for _, row in recent_matches.iterrows():
            match_html = f'<div class="match-card"><div><div class="match-date">{row.get("Date", "N/A")}</div><div class="match-teams">{row["Home"]} vs {row["Away"]}</div></div><div class="match-score">{row["HG"]} - {row["AG"]}</div></div>'
            st.markdown(match_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="match-date">date indisponibile</div>', unsafe_allow_html=True)

for col, league_name in zip(league_cols[1:], MOCK_LEAGUES.keys()):
    with col:
        st.markdown(f'<div class="league-col-title">{league_name}</div>', unsafe_allow_html=True)
        for m in MOCK_LEAGUES[league_name]:
            match_html = f'<div class="match-card"><div><div class="match-date">{m["Date"]}</div><div class="match-teams">{m["Home"]} vs {m["Away"]}</div></div><div class="match-score">{m["HG"]} - {m["AG"]}</div></div>'
            st.markdown(match_html, unsafe_allow_html=True)

st.write("")
st.divider()

# --- FUNCȚII INTEROGĂRI ---
def run_query(query_number, dataframe):
    if dataframe is None:
        return pd.DataFrame()
    if query_number == 1:
        return dataframe.groupby("Home")["AG"].sum().reset_index(name="Goluri_Primite_Acasa")
    if query_number == 2:
        return dataframe.groupby("Away")["HG"].sum().reset_index(name="Goluri_Primite_Deplasare")
    if query_number == 3:
        return dataframe[dataframe["Home"].astype(str).str.contains("Bucuresti", case=False)]
    if query_number == 4:
        return dataframe[dataframe["Away"].astype(str).str.contains("Bucuresti", case=False)]
    if query_number == 5:
        return dataframe[dataframe["HG"] > 2][["Home", "Away", "HG", "AG"]]

# --- FUNCȚIE AI CHAT / ANALIZĂ ---
def ask_ai_about_data(data_context, user_question):
    try:
        client = genai.Client(api_key=st.secrets["gemini"])
    except Exception as e:
        return f"Eroare la inițializarea Gemini: {e}"

    prompt = f"""
        You are SQLScout AI, an expert sports data analyst and professional football predictor.
        Here is the current dataset loaded from the application:
        {data_context}

        User question or request:
        {user_question}

        Provide a clear, professional, and structured response based strictly on the provided data.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Eroare la generarea răspunsului: {e}"

# --- MEMORIE INTERNĂ ---
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "current_query_name" not in st.session_state:
    st.session_state.current_query_name = ""

# --- MENIU SELECTARE LIGI  ---
st.markdown('<h3 style="text-align:center;">Selectare Ligă</h3>', unsafe_allow_html=True)
league_center_cols = st.columns([1, 2, 1])
with league_center_cols[1]:
    with st.container(key="league_buttons"):
        if st.button("Superliga României", key="superliga_btn"):
            pass
        if st.button("Gol", key="liga2_btn"):
            pass
        if st.button("Gol", key="cupa_btn"):
            pass
        if st.button("Gol", key="intl_btn"):
            pass

st.write("")

# --- PANOU INTEROGĂRI STATISTICE ---
st.subheader("Statistici")
stat_col_buttons, stat_col_table = st.columns([1, 3])

with stat_col_buttons:
    with st.container(key="stats_buttons"):
        if st.button("Goluri Primite Acasă"):
            st.session_state.current_df = run_query(1, df)
            st.session_state.current_query_name = "Total Goluri Primite de Echipele Gazdă"

        if st.button("Goluri Primite Deplasare"):
            st.session_state.current_df = run_query(2, df)
            st.session_state.current_query_name = "Total Goluri Primite de Echipele Oaspete"

        if st.button("București Acasă"):
            st.session_state.current_df = run_query(3, df)
            st.session_state.current_query_name = "Meciuri cu echipe din București jucând Acasă"

        if st.button("București Deplasare"):
            st.session_state.current_df = run_query(4, df)
            st.session_state.current_query_name = "Meciuri cu echipe din București jucând în Deplasare"

        if st.button("Gazde > 2 Goluri"):
            st.session_state.current_df = run_query(5, df)
            st.session_state.current_query_name = "Meciuri în care Gazda a marcat > 2 goluri"

with stat_col_table:
    if st.session_state.current_df is not None:
        result_df = st.session_state.current_df
        if result_df.empty:
            st.markdown('<div class="match-date">niciun rezultat</div>', unsafe_allow_html=True)
        else:
            headers_html = "".join(f"<th>{col}</th>" for col in result_df.columns)
            rows_html = ""
            for _, r in result_df.iterrows():
                cells_html = "".join(f"<td>{r[col]}</td>" for col in result_df.columns)
                rows_html += f"<tr>{cells_html}</tr>"
            table_html = f'<div class="table-scroll-wrapper"><table class="compact-table"><thead><tr>{headers_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)

# --- ZONA DE JOS: CHAT AI INTERACTIV ---
if st.session_state.current_df is not None:
    st.write("")
    st.divider()
    st.subheader("Asistent AI SQLScout")
    with st.container(border=True):
        st.markdown("Pune o întrebare liberă despre datele afișate mai sus!")

        user_prompt = st.text_input("Întreabă AI-ul :")

        if st.button("Trimite Întrebarea Către AI", type="primary"):
            if user_prompt.strip() == "":
                st.warning("Te rog să introduci o cerere sau o întrebare.")
            else:
                limited_data = st.session_state.current_df.head(30).to_csv(index=False)
                with st.spinner("SQLScout AI analizează datele..."):
                    answer = ask_ai_about_data(limited_data, user_prompt)
                st.success("Răspuns generat:")
                st.markdown(answer)