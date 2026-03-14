import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('qumail.db', check_same_thread=False)
    c = conn.cursor()
    # Table for Emails (including attachments)
    c.execute('''CREATE TABLE IF NOT EXISTS emails 
                 (id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, subject TEXT, 
                  body_ciphertext TEXT, key_id TEXT, timestamp TEXT,
                  filename TEXT, file_blob BLOB)''')
    
    # Table for Keys (Simulating Hardware)
    c.execute('''CREATE TABLE IF NOT EXISTS quantum_keys 
                 (key_id TEXT PRIMARY KEY, key_value TEXT)''')
                 
    # Simulation State Table (Alice, Bob, Hacker shared state)
    c.execute('''CREATE TABLE IF NOT EXISTS simulation_state
                 (key TEXT PRIMARY KEY, value TEXT)''')
                 
    # Initialize Hacker state if it doesn't exist
    c.execute('''INSERT OR IGNORE INTO simulation_state (key, value) VALUES ('hacker_listening', '0')''')
    
    # Hacker Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS hacker_logs
                 (id INTEGER PRIMARY KEY, timestamp TEXT, sender TEXT, receiver TEXT, intercepted_data TEXT)''')
                 
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

def save_email(sender, receiver, subject, ciphertext, key_id, filename=None, file_data=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""INSERT INTO emails 
                 (sender, receiver, subject, body_ciphertext, key_id, timestamp, filename, file_blob) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (sender, receiver, subject, ciphertext, key_id, timestamp, filename, file_data))
    conn.commit()

def get_inbox(user_email):
    c.execute("SELECT * FROM emails WHERE receiver = ? ORDER BY id DESC", (user_email,))
    return c.fetchall()

def get_sent_box(user_email):
    c.execute("SELECT * FROM emails WHERE sender = ? ORDER BY id DESC", (user_email,))
    return c.fetchall()

def get_key(key_id):
    c.execute("SELECT key_value FROM quantum_keys WHERE key_id = ?", (key_id,))
    result = c.fetchone()
    return result[0] if result else None

def store_key(key_id, key_value):
    conn = sqlite3.connect('qumail.db')
    c = conn.cursor()
    
    c.execute("INSERT OR IGNORE INTO quantum_keys (key_id, key_value) VALUES (?, ?)", (key_id, key_value))
    
    conn.commit()
    conn.close()

# --- HACKER SIMULATION FUNCTIONS ---

def set_hacker_listening(is_listening: bool):
    conn = sqlite3.connect('qumail.db', check_same_thread=False)
    c = conn.cursor()
    val = "1" if is_listening else "0"
    c.execute("UPDATE simulation_state SET value = ? WHERE key = 'hacker_listening'", (val,))
    conn.commit()
    conn.close()

def is_hacker_listening() -> bool:
    conn = sqlite3.connect('qumail.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT value FROM simulation_state WHERE key = 'hacker_listening'")
    result = c.fetchone()
    conn.close()
    return result[0] == "1" if result else False

def log_intercept(sender, receiver, data):
    conn = sqlite3.connect('qumail.db', check_same_thread=False)
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO hacker_logs (timestamp, sender, receiver, intercepted_data) VALUES (?, ?, ?, ?)",
              (timestamp, sender, receiver, data))
    conn.commit()
    conn.close()

def get_hacker_logs():
    conn = sqlite3.connect('qumail.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM hacker_logs ORDER BY id DESC")
    results = c.fetchall()
    conn.close()
    return results