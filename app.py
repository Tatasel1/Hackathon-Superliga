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

if st.sidebar.button("Run Query"):
    df = run_query("SELECT * FROM dbo.Romania_dest WHERE Away LIKE '%Bucuresti%'")
    st.dataframe(df)
    
    
st.sidebar.write("Enter your SQL query below:")
user_query = st.sidebar.text_area("SQL Query", height=150)

# PARTEA CU API DE GERMINI
client = genai.Client(api_key=st.secrets["api_key"])

response = client.responses.create(
    model="gemini-2.5-flash",
    input=f"Please analyze the following SQL query and provide insights: {user_query}"
)

st.sidebar.write("API Response:")
st.sidebar.write(response.choices[0].message)