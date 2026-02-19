import sqlite3
import os
from datetime import datetime

def save_application(name, income, loan_amount, risk_score, status):
    # Ensure the data folder exists
    os.makedirs('data', exist_ok=True)
    
    # Connect to the EXACT same database the Dashboard uses
    conn = sqlite3.connect('data/applications.db')
    cursor = conn.cursor()
    
    # Create the table safely if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            income REAL,
            loan_amount REAL,
            risk_score REAL,
            status TEXT,
            timestamp TEXT
        )
    ''')
    
    # Insert the new application
    cursor.execute('''
        INSERT INTO applications (name, income, loan_amount, risk_score, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, income, loan_amount, risk_score, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
