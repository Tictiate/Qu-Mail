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
    c.execute("INSERT INTO quantum_keys (key_id, key_value) VALUES (?, ?)", (key_id, key_value))
    conn.commit()