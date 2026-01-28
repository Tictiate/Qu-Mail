from cryptography.fernet import Fernet
import secrets
from . import db # Import our database manager

def generate_quantum_key():
    """Simulates the Quantum Channel (ETSI 014)."""
    key = Fernet.generate_key()
    key_id = f"QID-{secrets.token_hex(4).upper()}"
    
    # Store in the "Hardware Vault" (Database) so Bob can find it later
    db.store_key(key_id, key.decode())
    
    return key_id, key

def encrypt_content(content, key):
    f = Fernet(key)
    return f.encrypt(content.encode()).decode()

def decrypt_content(ciphertext, key_id):
    # 1. Ask the Key Manager for the key
    key_str = db.get_key(key_id)
    
    if not key_str:
        return "❌ CRITICAL SECURITY ALERT: Quantum Key Discarded or Not Found."
    
    # 2. Decrypt
    try:
        f = Fernet(key_str.encode())
        return f.decrypt(ciphertext.encode()).decode()
    except:
        return "❌ ERROR: Decryption failed. Data corrupted."

def encrypt_file_bytes(file_bytes, key):
    """Encrypts raw bytes (like a PDF or Image)."""
    f = Fernet(key)
    return f.encrypt(file_bytes)

def decrypt_file_bytes(encrypted_bytes, key_id):
    """Decrypts raw bytes using the stored key."""
    key_str = db.get_key(key_id)
    if not key_str:
        return None
    try:
        f = Fernet(key_str.encode())
        return f.decrypt(encrypted_bytes)
    except:
        return None