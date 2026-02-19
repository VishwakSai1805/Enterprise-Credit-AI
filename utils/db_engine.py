import sqlite3
import pandas as pd
import os

# Create data folder if missing
if not os.path.exists('data'):
    os.makedirs('data')

DB_NAME = "data/credit_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  income REAL,
                  loan_amount REAL,
                  risk_score REAL,
                  status TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_application(name, income, loan_amount, risk_score, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO applications (name, income, loan_amount, risk_score, status) VALUES (?, ?, ?, ?, ?)",
              (name, income, loan_amount, risk_score, status))
    conn.commit()
    conn.close()

def load_all_applications():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM applications", conn)
    conn.close()
    return df
