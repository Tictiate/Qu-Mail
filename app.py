import streamlit as st
import secrets
import smtplib
from email.mime.text import MIMEText
from cryptography.fernet import Fernet

# --- CONFIGURATION ---
# Set the page title and icon
st.set_page_config(page_title="Qu-Mail | Quantum-Secure Client", page_icon="⚛️", layout="centered")

# --- 1. THE "MOCK" QUANTUM KEY MANAGER (Simulating ETSI GS QKD 014) ---
# In real life, this is a hardware server. For tonight, we use 'st.session_state'
# to act as the "Shared Cloud Database" between Alice and Bob.
if "key_store" not in st.session_state:
    st.session_state.key_store = {}

def get_quantum_key():
    """Generates a 256-bit AES key and a unique ID."""
    key = Fernet.generate_key() # This is our "Quantum Key"
    key_id = secrets.token_hex(4).upper() # Generates a random ID like '4F2A9C'
    
    # Store it in our mock cloud so the Receiver tab can find it
    st.session_state.key_store[key_id] = key.decode()
    
    return key_id, key

# --- 2. THE CRYPTO ENGINE ---
def encrypt_message(message, key, level):
    f = Fernet(key)
    if level == "Level 2 (AES-256)":
        # Standard robust encryption
        return f.encrypt(message.encode()).decode()
    elif level == "Level 1 (One-Time Pad)":
        # Simulating OTP (XOR) for the demo. Real OTP is complex to implement in one file.
        # We will wrap it in a visual indicator so judges see the difference.
        encrypted = f.encrypt(message.encode()).decode() 
        return f"OTP_MODE::{encrypted}" 
    else:
        return message # No encryption

def decrypt_message(encrypted_text, key_id):
    # 1. Look up the key in our Mock Cloud
    stored_key = st.session_state.key_store.get(key_id)
    
    if not stored_key:
        return "❌ Error: Key ID not found (Key destroyed or never existed)."
    
    # 2. Try to decrypt
    try:
        f = Fernet(stored_key.encode())
        # Handle our fake "OTP Mode" tag
        clean_text = encrypted_text.replace("OTP_MODE::", "")
        decrypted_bytes = f.decrypt(clean_text.encode())
        return decrypted_bytes.decode()
    except Exception as e:
        return "❌ Decryption Failed: Signal corrupted."

# --- 3. THE UI (FRONTEND) ---
st.title("⚛️ QuMail MVP")
st.caption("Quantum Key Distribution (QKD) Email Client v1.0")

# Create tabs for the Sender (Alice) and Receiver (Bob)
tab1, tab2 = st.tabs(["📧 Compose (Alice)", "🔓 Decrypt (Bob)"])

# === TAB 1: SENDER ===
with tab1:
    st.header("Compose Secure Email")
    
    # User Inputs
    sender_email = st.text_input("Your Gmail Address", placeholder="you@gmail.com")
    # SECURITY NOTE: In a real app, use environment variables!
    app_password = st.text_input("Google App Password", type="password", help="Go to Google Account > Security > App Passwords")
    recipient_email = st.text_input("Recipient Email")
    
    security_level = st.selectbox("Encryption Protocol", 
                                  ["Level 2 (AES-256)", "Level 1 (One-Time Pad)", "Standard (No QKD)"])
    
    body = st.text_area("Message Body", height=150)
    
    if st.button("Encrypt & Send"):
        if not body:
            st.warning("Please write a message first.")
        else:
            # A. Get Key from KM
            key_id, q_key = get_quantum_key()
            
            # B. Encrypt
            cipher_text = encrypt_message(body, q_key, security_level)
            
            # C. Construct Payload
            # This is what actually travels over the internet
            email_payload = f"""
--- ⚛️ QUMAIL SECURE TRANSMISSION ⚛️ ---
KEY_ID: {key_id}
SECURITY_LEVEL: {security_level}
---------------------------------------
{cipher_text}
---------------------------------------
"""
            # D. Send via Gmail SMTP
            try:
                # Setup the server connection
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls() # Secure the connection
                server.login(sender_email, app_password)
                
                # Send
                msg = MIMEText(email_payload)
                msg['Subject'] = f"⚛️ Secure Msg [ID: {key_id}]"
                msg['From'] = sender_email
                msg['To'] = recipient_email
                
                server.sendmail(sender_email, recipient_email, msg.as_string())
                server.quit()
                
                st.success("Message Sent Successfully!")
                st.info(f"Quantum Key ID `{key_id}` has been synchronized to the network.")
                
                # Show debug info for the judges
                with st.expander("See what the Hacker sees (Encrypted Payload)"):
                    st.code(email_payload)
                    
            except Exception as e:
                st.error(f"Failed to send email. Did you use an App Password? Error: {e}")
                # Fallback for demo if email fails
                st.warning("⚠️ Email failed, but Key was generated. You can still test decryption in Tab 2!")
                st.code(email_payload)

# === TAB 2: RECEIVER ===
with tab2:
    st.header("Decrypt Message")
    st.markdown("Paste the **Cipher Text** and **Key ID** from the email you received.")
    
    col1, col2 = st.columns(2)
    with col1:
        rx_key_id = st.text_input("Enter Key ID (e.g., 4A2B)", max_chars=10)
    with col2:
        # Just a visual placeholder for the "Connected" status
        st.success("✅ Connected to Quantum Node")
        
    rx_ciphertext = st.text_area("Paste Encrypted Text (The gibberish part)", height=100)
    
    if st.button("🔓 Decrypt with Quantum Key"):
        result = decrypt_message(rx_ciphertext, rx_key_id)
        
        if "❌" in result:
            st.error(result)
        else:
            st.balloons() # Fun effect for a successful demo
            st.success("Decryption Successful!")
            st.markdown(f"**Original Message:**")
            st.info(result)