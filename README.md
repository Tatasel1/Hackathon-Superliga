# ⚽ Football Data Assistant

This project is a Streamlit-based web application that analyzes football data from the Romanian Superliga. It connects to a SQL Server database, executes complex queries, and uses the Gemini AI API to provide intelligent insights on the data.

## ⚙️ Prerequisites

- **Python 3.8+** installed on your machine.
- **SQL Server** (or access to the cloud database) with the `ROU` dataset populated.
- **ODBC Driver 17 for SQL Server** installed (required for the `pyodbc` library).

---

## 🚀 Setup & Installation Guide

Follow these steps to set up the project locally.

### 1. Clone the repository

Open your terminal and clone the repository (if you haven't already), then navigate into the project folder:

```bash
git clone <your-repo-url-here>
cd <your-project-folder-name>
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Depending on your operating system, run one of the following commands:

**For Windows (Command Prompt / PowerShell):**

```bash
venv\Scripts\activate
```

> **Note:** If you get an execution policy error in PowerShell, run `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` and try again.

**For macOS / Linux:**

```bash
source venv/bin/activate
```

You should now see `(venv)` at the beginning of your terminal prompt.

### 4. Install Dependencies

With the virtual environment activated, install all the required Python packages (Streamlit, Pandas, PyODBC, Google Generative AI) using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 5. Database & API Configuration

Before starting the app, you need to configure your local credentials:

1. Open `app.py`.
2. Locate the `init_connection()` function.
3. Update the `SERVER`, `DATABASE`, `UID`, and `PWD` variables to match your SQL Server setup.
4. *(Optional for now)* Add your Gemini API Key when prompted in the code.

---

## 💻 Running the Application

To start the Streamlit server and view the web interface, run the following command in your terminal:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at [http://localhost:8501](http://localhost:8501).

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) - Web framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [PyODBC](https://github.com/mkleehammer/pyodbc) - SQL Server connection
- [Google Gemini API](https://ai.google.dev/) - AI analysis
