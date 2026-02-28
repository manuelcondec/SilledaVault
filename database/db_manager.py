import sqlite3

DB_PATH = 'vault.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY, salt BLOB, v_nonce BLOB, v_tag BLOB, 
                p_cipher BLOB, p_nonce BLOB, intentos INTEGER, bloqueo REAL)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT, service_id TEXT UNIQUE, 
                s_c BLOB, s_n BLOB, u_c BLOB, u_n BLOB, p_c BLOB, p_n BLOB, honey INTEGER)
        """)