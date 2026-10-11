import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.expanduser("~/smart_attendance_system/data/attendance.db")
EXCEL_DIR = os.path.expanduser("~/smart_attendance_system/data/exports")

def init_db():
    """Local Database ???????? ??????? ?????????????"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(EXCEL_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT,
            sync_status INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def log_attendance_locally(student_name, confidence, image_path):
    """?????????????? Local DB ???? ????????? Duplicate ????????????"""
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ?????????????? ?????????????? ???????????? ???????????
    cursor.execute('''
        SELECT id FROM attendance_logs 
        WHERE student_name = ? AND date = ?
    ''', (student_name, current_date))
    
    if cursor.fetchone() is not None:
        conn.close()
        return False  # Already marked today

    cursor.execute('''
        INSERT INTO attendance_logs (student_name, date, time, confidence, image_path, sync_status)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (student_name, current_date, current_time, confidence, image_path))
    conn.commit()
    conn.close()

    # Offline Excel ??????????? ?????????????????
    export_to_excel(current_date)
    return True

def export_to_excel(target_date):
    """??????????????????? ????????????? Excel ?????????? ???????????"""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT student_name, date, time, confidence, sync_status FROM attendance_logs WHERE date = '{target_date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        excel_file = os.path.join(EXCEL_DIR, f"Attendance_{target_date}.xlsx")
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"[OFFLINE BACKUP] Excel generated: {excel_file}")
