import streamlit as st
import pyodbc
import pandas as pd
import time
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
    </style>
""", unsafe_allow_html=True)

# --- HEADER CENTRAT ---
st.markdown('<p class="centered-title">SQLScout</p>', unsafe_allow_html=True)
st.divider()

# --- INITIALIZARE CONEXIUNE BAZA DE DATE ---
@st.cache_resource
def init_connection():
    try:
        server = st.secrets["server"]
        database = st.secrets["database"]
        username = st.secrets["username"]
        password = st.secrets["password"]
        conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Connection Timeout=30;"
        return pyodbc.connect(conn_str)
    except Exception as e:
        st.error(f"Eroare la conectarea la baza de date: {e}")
        return None

conn = init_connection()

if "db_connected" not in st.session_state:
    if conn:
        placeholder = st.empty()
        placeholder.success("Connected to the database successfully!")
        time.sleep(1)
        placeholder.empty()
        st.session_state.db_connected = True
    else:
        st.session_state.db_connected = False

def run_query(query):
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

# --- FUNCȚIE AI CHAT / ANALIZĂ STRUCTURATĂ ---
def analyze_data(data):
    try:
        client = genai.Client(api_key=st.secrets["gemini"])
    except Exception as e:
        return f"Eroare la inițializarea Gemini: {e}"

    prompt = f"""
        You are an expert sports data analyst and professional football predictor. 

        I have executed a specific SQL query on a historical database containing match results, goals, and betting odds. 

        Here is the data returned by the database (limited to a max of 30 rows):
        {data}

        Based on this dataset, please provide a comprehensive and structured analysis following exactly these sections:
        1. 📊 Executive Summary (Provide a concise overview...)
        2. 🔍 Deep Data Analysis & Trends (Identify key patterns...)
        3. 🔮 Future Prospects & Predictions (What can we expect...)
        4. 💡 Actionable Insights (Translate findings into betting/analytical advice...)

        Keep the tone professional, objective, and analytical. Use bullet points and bold text.
        Please ensure that your analysis is based solely on the data provided and does not include any external information or assumptions.
    """
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
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

# --- BARA LATERALĂ: CUSTOM QUERY ---
st.sidebar.title("Interfață SQL Custom")
st.sidebar.write("Rulează propriul query pe baza de date:")
user_query = st.sidebar.text_area("SQL Query", height=150)

if st.sidebar.button("Rulează Query Custom"):
    if user_query.strip() == "":
        st.sidebar.warning("Te rog să introduci un query SQL!")
    else:
        try:
            st.session_state.current_df = run_query(user_query)
            st.session_state.current_query_name = "Rezultate Custom Query"
        except Exception as e:
            st.sidebar.error(f"Eroare de execuție: {e}")

# --- PANOU INTEROGĂRI STATISTICE ---
st.subheader("Interogări SQL Rapide")
stat_col_buttons, stat_col_table = st.columns([1, 3])

with stat_col_buttons:
    with st.container(key="stats_buttons"):
        if st.button("Echipe din București oaspete (Toate datele)"):
            try:
                query = "SELECT * FROM dbo.Romania_dest WHERE Away LIKE '%Bucuresti%'"
                st.session_state.current_df = run_query(query)
                st.session_state.current_query_name = "Toate meciurile cu echipe din București jucând în deplasare"
            except Exception as e:
                st.error(f"Eroare SQL: {e}")

        if st.button("Echipe din București gazde (Date, Home, Away, HG, AG, Res)"):
            try:
                query = "SELECT Date, Home, Away, HG, AG, Res FROM dbo.Romania_dest WHERE Home LIKE '%Bucuresti%'"
                st.session_state.current_df = run_query(query)
                st.session_state.current_query_name = "Date esențiale: București Acasă"
            except Exception as e:
                st.error(f"Eroare SQL: {e}")

        if st.button("Norvegia (Egaluri)"):
            try:
                query = "SELECT * FROM dbo.Norway_dest WHERE HG = AG"
                st.session_state.current_df = run_query(query)
                st.session_state.current_query_name = "Meciuri terminate la egalitate în Norvegia"
            except Exception as e:
                st.error(f"Eroare SQL: {e}")

        if st.button("Finlanda (Cota medie < 2.3 Drept Gazda)"):
            try:
                query = "SELECT Home, AVG(AvgCH) as Cota_Medie_Acasa FROM dbo.Finland_dest GROUP BY Home HAVING AVG(AvgCH) < 2.3"
                st.session_state.current_df = run_query(query)
                st.session_state.current_query_name = "Echipe Finlanda cu cotă medie acasă sub 2.3"
            except Exception as e:
                st.error(f"Eroare SQL: {e}")

        if st.button("România (>250 Goluri Marcate Drept Gazda)"):
            try:
                query = "SELECT HOME, sum(HG) as Goluri_Marcate FROM dbo.Romania_dest GROUP BY Home HAVING SUM(HG) > 250"
                st.session_state.current_df = run_query(query)
                st.session_state.current_query_name = "Echipe din România cu peste 250 de goluri marcate acasă"
            except Exception as e:
                st.error(f"Eroare SQL: {e}")

with stat_col_table:
    if st.session_state.current_df is not None:
        result_df = st.session_state.current_df
        if result_df.empty:
            st.markdown('<div class="match-date">Niciun rezultat returnat din baza de date.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**{st.session_state.current_query_name}**")
            headers_html = "".join(f"<th>{col}</th>" for col in result_df.columns)
            rows_html = ""
            for _, r in result_df.head(100).iterrows():
                cells_html = "".join(f"<td>{r[col]}</td>" for col in result_df.columns)
                rows_html += f"<tr>{cells_html}</tr>"
            table_html = f'<div class="table-scroll-wrapper"><table class="compact-table"><thead><tr>{headers_html}</tr></thead><tbody>{rows_html}</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)

# --- ZONA DE JOS: RAPORT AI INTERACTIV ---
if st.session_state.current_df is not None and not st.session_state.current_df.empty:
    st.write("")
    st.divider()
    st.subheader("Asistent AI SQLScout - Raport Profesionist")
    with st.container(border=True):
        st.markdown("Generează o analiză sportivă pe baza datelor afișate mai sus (maxim 30 de rânduri analizate).")

        if st.button("Generează Analiza Datelor", type="primary"):
            limited_data = st.session_state.current_df.head(30)
            with st.spinner("AI-ul analizează tendințele..."):
                answer = analyze_data(limited_data.to_csv(index=False))
            
            st.success("Analiză generată cu succes:")
            st.markdown(answer)