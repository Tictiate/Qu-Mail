from cryptography.fernet import Fernet
import base64

def generate_quantum_key():
    """Generates a random 32-byte key, returns (key_id, key_bytes)"""
    key = Fernet.generate_key()
    key_id = base64.urlsafe_b64encode(key[:6]).decode()  # Short ID for reference
    return key_id, key

def encrypt_content(message, key):
    """Encrypts text. Accepts key as bytes or string (URL-safe base64)."""
    try:
        # 1. Handle Key Format
        # Fernet keys are URL-safe base64-encoded, so convert string to bytes directly
        if isinstance(key, str):
            key = key.strip()  # Remove whitespace that might have been added
            key = key.encode('utf-8') if isinstance(key, str) else key
            
        f = Fernet(key)
        
        # 2. Encrypt
        cipher_bytes = f.encrypt(message.encode('utf-8'))
        return cipher_bytes.decode('utf-8') # Return as string for JSON/Email
    except Exception as e:
        return f"❌ Encryption Error: {str(e)}"

def decrypt_content(ciphertext, key):
    """Decrypts text. Accepts inputs as bytes or string (URL-safe base64)."""
    try:
        # 1. Handle Key Format
        # Key should be URL-safe base64-encoded string/bytes
        if isinstance(key, str):
            key = key.strip()  # Remove all surrounding whitespace
            key = key.encode('utf-8')
            
        # 2. Handle Ciphertext Format
        if isinstance(ciphertext, str):
            # IMPORTANT: Remove all newlines/spaces that might have been copied
            ciphertext = ciphertext.replace(" ", "").replace("\n", "").replace("\r", "").strip()
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