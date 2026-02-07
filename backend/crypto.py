from cryptography.fernet import Fernet
import base64

def generate_quantum_key():
    """Generates a random 32-byte key, returns (key_id, key_bytes)"""
    key = Fernet.generate_key()
    key_id = base64.urlsafe_b64encode(key[:6]).decode()  # Short ID for reference
    return key_id, key

def encrypt_content(message, key):
    """Encrypts text. Accepts key as bytes or string."""
    try:
        # 1. Force Key to Bytes
        if isinstance(key, str):
            key = key.encode('utf-8')
            
        f = Fernet(key)
        
        # 2. Encrypt
        cipher_bytes = f.encrypt(message.encode('utf-8'))
        return cipher_bytes.decode('utf-8') # Return as string for JSON/Email
    except Exception as e:
        return f"❌ Encryption Error: {str(e)}"

def decrypt_content(ciphertext, key):
    """Decrypts text. Accepts inputs as bytes or string."""
    try:
        # 1. Force Key to Bytes
        if isinstance(key, str):
            key = key.strip().encode('utf-8') # Strip whitespace and encode
            
        # 2. Force Ciphertext to Bytes
        if isinstance(ciphertext, str):
            # IMPORTANT: Remove all newlines/spaces that might have been copied
            ciphertext = ciphertext.replace(" ", "").replace("\n", "").replace("\r", "")
            ciphertext = ciphertext.encode('utf-8')

        f = Fernet(key)
        decrypted_bytes = f.decrypt(ciphertext)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # This is what you see in the UI
        return f"❌ Decrypt Error: {str(e)}"

# --- FILE HANDLING (Keep this same logic) ---
def encrypt_file_bytes(file_data, key):
    if isinstance(key, str): key = key.encode('utf-8')
    f = Fernet(key)
    return f.encrypt(file_data)

def decrypt_file_bytes(encrypted_data, key):
    try:
        if isinstance(key, str): key = key.encode('utf-8')
        f = Fernet(key)
        return f.decrypt(encrypted_data)
    except:
        return None