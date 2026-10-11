import sqlite3
import time
import os
import threading
import socket
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DB_PATH = os.path.expanduser("~/smart_attendance_system/data/attendance.db")
CREDS_FILE = os.path.expanduser("~/smart_attendance_system/credentials.json")
SHEET_NAME = "Student_Attendance"

def is_connected_to_internet():
    """Internet connection ??????? ping ???????????"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def sync_pending_records():
    if not is_connected_to_internet():
        return

    if not os.path.exists(CREDS_FILE):
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, student_name, date, time, confidence 
        FROM attendance_logs 
        WHERE sync_status = 0
    ''')
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1

        for row in rows:
            record_id, name, log_date, log_time, conf = row
            sheet.append_row([log_date, log_time, name, "Present", f"{int(conf*100)}%"])
            
            # DB ???? Sync ??????????? ?????????????????
            cursor.execute("UPDATE attendance_logs SET sync_status = 1 WHERE id = ?", (record_id,))
            conn.commit()

        print(f"[CLOUD SYNC] Successfully synced {len(rows)} records to Google Sheets.")
    except Exception as e:
        print(f"[SYNC ERROR] {e}")
    finally:
        conn.close()

def start_auto_sync_thread(interval_sec=30):
    def worker():
        while True:
            sync_pending_records()
            time.sleep(interval_sec)
    
    t = threading.Thread(target=worker, daemon=True)
    t.start()
