import streamlit as st
import pyodbc
import pandas as pd
from google import genai
import time

def init_connection():
    server = st.secrets["server"]
    database = st.secrets["database"]
    username = st.secrets["username"]
    password = st.secrets["password"]
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection = yes"
    return pyodbc.connect(conn_str)

conn = init_connection()
if conn:
    placeholder = st.empty()
    placeholder.success("Connected to the database successfully!")
    time.sleep(1)
    placeholder.empty()
else:
    st.error("Failed to connect to the database.")

def run_query(query):
    return pd.read_sql(query, conn)
    
st.write("HELLO WORLD!!")

st.sidebar.title("Database Query Interface")

# --- INITIALIZARE MEMORIE STREAMLIT ---
if "current_df" not in st.session_state:
    st.session_state.current_df = None

# The function that handles the AI generation
def analyze_data(data):
    try:
        client = genai.Client(api_key=st.secrets["gemini"])
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        return "Error initializing Gemini client."

    prompt = f"""
        You are an expert sports data analyst and professional football predictor, specializing in the Romanian Superliga. 

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
        st.error(f"Error generating AI analysis: {e}")
        return "Error generating AI analysis."


# --- MENIUL DIN STÂNGA (Aici doar salvăm datele în memorie) ---

if st.sidebar.button("Query 1"):
    try:
        st.session_state.current_df = run_query("SELECT Home, SUM(AG) as Total_AG FROM dbo.Romania_dest GROUP BY Home")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
    
if st.sidebar.button("Query 2"):
    try:
        st.session_state.current_df = run_query("SELECT Home, SUM(AG) as Total_AG FROM dbo.Romania_dest GROUP BY Home")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("Query 3"):
    try:
        st.session_state.current_df = run_query("SELECT * FROM dbo.Romania_dest WHERE Home LIKE '%Bucuresti%'")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("Query 4"):
    try:
        st.session_state.current_df = run_query("SELECT * FROM dbo.Romania_dest WHERE Away LIKE '%Bucuresti%'")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.sidebar.button("Query 5"):
    try:
        st.session_state.current_df = run_query("SELECT Home, Away, HG, AG FROM dbo.Romania_dest WHERE HG > 2")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --- CUSTOM QUERY ---
st.sidebar.write("Enter your SQL query below:")
user_query = st.sidebar.text_area("SQL Query", height=150)

if st.sidebar.button("Run Custom Query"):
    if user_query.strip() == "":
        st.sidebar.warning("Please enter a query first!")
    else:
        try:
            st.session_state.current_df = run_query(user_query) 
        except Exception as e:
            st.sidebar.error(f"Execution error: {e}")


# --- ECRANUL PRINCIPAL (Afișarea tabelului și butonul AI) ---
if st.session_state.current_df is not None:
    st.write("### Query Results")
    st.dataframe(st.session_state.current_df)

    limited_data = st.session_state.current_df.head(30)
    
    # Butonul este acum pe ecranul principal
    if st.button("Analyze Data with AI"):
        with st.spinner("AI is analyzing the data..."): 
            res = analyze_data(limited_data.to_csv(index=False))
        st.write("### AI Analysis:")
        st.write(res)