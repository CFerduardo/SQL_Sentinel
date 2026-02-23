import sqlite3
from datetime import datetime
from pathlib import Path

import pyodbc
from loguru import logger

from config.settings import (SQL_TIMEOUT, UMBRAL_DISCO_MIN_PCT,
                             UMBRAL_LOG_MAX_PCT)
from src.checks import QUERY_DISCOS, QUERY_LOGS

# --- route configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "sentinel.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

logger.add(BASE_DIR / "logs" / "monitor.log", rotation="10 MB", level="INFO")

def initialize_database():
    """Create the local table for the monitoring history if it does not exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT, 
            date DATETIME, 
            status TEXT,
            critical_disc TEXT, 
            critical_log TEXT, 
            error_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_event(store, status, disc_info="", log_info="", error=""):
    """Save the result of each check in the local database"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO monitoring_history (store, date, status, critical_disc, critical_log, error_msg)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (store, datetime.now(), status, disc_info, log_info, error))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error writing to SQLite: {e}")

def last_connection(store):
    """Retrieve the last time the server was online for the report"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT date FROM monitoring_history WHERE store = ? AND status = "ONLINE" ORDER BY date DESC LIMIT 1', (store,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "without registration"

def check_sql_server_global(config):

    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={config['SERVER']};"
        f"DATABASE=master;UID={config['USER']};PWD={config['PASS']};"
        f"Connection Timeout={SQL_TIMEOUT};"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Hard Drive Monitoring
        cursor.execute(QUERY_DISCOS)
        discos = cursor.fetchall()
        # Filter only the disks that are below the configured threshold
        alert_discs = [f"{d[0]} ({float(d[1]):.1f}%)" for d in discos if d[1] < UMBRAL_DISCO_MIN_PCT]
        
        cursor.execute(QUERY_LOGS)
        logs = cursor.fetchall()
        
        final_logs = []
        for l in logs:
            db_name = l[0]      # database name
            if l[1] is None or l[2] is None or l[1] == 0:
                continue
            
            total_mb = float(l[1])
            used_mb = float(l[2])
            pct_used = (used_mb / total_mb) * 100
            
            if pct_used > UMBRAL_LOG_MAX_PCT:
                final_logs.append(f"{db_name} ({pct_used:.1f}%)")
        
        conn.close()
        return {
            "status": "ONLINE", 
            "critical_disc": ", ".join(alert_discs), 
            "critical_log": ", ".join(final_logs),
            "error": ""
        }
    except Exception as e:
        logger.warning(f"headquarters OFFLINE: {config['name_headquarters']} -> {str(e)}")
        return {
            "status": "OFFLINE", 
            "critical_disc": "", 
            "critical_log": "", 
            "error": str(e)
        }