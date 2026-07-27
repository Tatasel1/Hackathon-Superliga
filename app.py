import streamlit as st
import pyodbc
import pandas as pd
from google import genai

def init_connection():
    server = st.secrets["server"]
    database = st.secrets["database"]
    username = st.secrets["username"]
    password = st.secrets["password"]
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection = yes"
    return pyodbc.connect(conn_str)

conn = init_connection()
if conn:
    st.success("Connected to the database successfully!")
else:
    st.error("Failed to connect to the database.")

def run_query(query):
    return pd.read_sql(query, conn)
    
    
st.write("BUNA PULA!!")

st.sidebar.title("Database Query Interface")

if st.sidebar.button("Query 1"):
    df = run_query("SELECT * FROM dbo.Romania_dest WHERE Away LIKE '%Bucuresti%'")
    st.dataframe(df)

if st.sidebar.button("Query 2"):
    df = run_query("SELECT Away, SUM(GA)  FROM dbo.Romania_dest GROUP BY HOME")
    st.dataframe(df)

if st.sidebar.button("Query 3"):
    df = run_query("SELECT * FROM dbo.Romania_dest WHERE Home LIKE '%Bucuresti%'")
    st.dataframe(df)

if st.sidebar.button("Query 4"):
    df = run_query("SELECT * FROM dbo.Romania_dest WHERE Home LIKE '%Bucuresti%'")
    st.dataframe(df)

if st.sidebar.button("Query 5"):
    df = run_query("SELECT * FROM dbo.Romania_dest WHERE Home LIKE '%Bucuresti%'")
    st.dataframe(df)

# 1. Put the text area FIRST so the user can type before clicking
st.sidebar.write("Enter your SQL query below:")
user_query = st.sidebar.text_area("SQL Query", height=150)

# 2. Add the button AFTER the text box
if st.sidebar.button("Run Custom Query"):
    
    # Check if the user actually typed something
    if user_query.strip() == "":
        st.sidebar.warning("Please enter a query first!")
    else:
        # --- RUN THE DATABASE QUERY ---
        try:
            # We use the user_query variable here instead of the hardcoded string
            df = run_query(user_query) 
            st.write("### Query Results")
            st.dataframe(df)
        except Exception as e:
            st.error(f"SQL Error: {e}")
            
        # --- RUN THE GEMINI API ---
        try:
            client = genai.Client(api_key=st.secrets["api_key"])
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Please analyze the following SQL query and provide insights: {user_query}"
            )
            st.sidebar.write("### AI Analysis:")
            st.sidebar.write(response.text)
        except Exception as e:
            st.sidebar.error(f"API Error: {e}")

