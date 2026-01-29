import socket
import json
import threading
from . import db

# Port to listen on (Arbitrary, but must match on both PCs)
PORT = 5005 

def start_server(update_callback):
    """
    Bob runs this to listen for incoming emails.
    update_callback: A function to refresh the UI when mail arrives.
    """
    def listener():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 0.0.0.0 means "Listen to everyone on the Wi-Fi"
        server_socket.bind(('0.0.0.0', PORT)) 
        server_socket.listen(5)
        print(f"👂 Listening for Quantum Mail on Port {PORT}...")
        
        while True:
            client, addr = server_socket.accept()
            print(f"📡 Connection from {addr}")
            
            try:
                # 1. Receive Data (up to 10MB buffer for attachments)
                data = b""
                while True:
                    packet = client.recv(4096)
                    if not packet: break
                    data += packet
                
                # 2. Parse JSON
                email_data = json.loads(data.decode('utf-8'))
                
                # 3. Save to Local DB (Bob's DB)
                # Note: We convert file_blob back to bytes if it exists
                file_blob = bytes.fromhex(email_data['file_hex']) if email_data.get('file_hex') else None
                
                db.save_email(
                    sender=email_data['sender'],
                    receiver=email_data['receiver'],
                    subject=email_data['subject'],
                    ciphertext=email_data['body'],
                    key_id=email_data['key_id'],
                    filename=email_data.get('filename'),
                    file_data=file_blob
                )
                
                # 4. Save the Key (Simulating QKD Hardware Sync)
                db.store_key(email_data['key_id'], email_data['key_value'])
                
                # 5. Tell UI to refresh
                if update_callback:
                    update_callback()
                    
            except Exception as e:
                print(f"❌ Network Error: {e}")
            finally:
                client.close()

    # Run listener in background so UI doesn't freeze
    t = threading.Thread(target=listener, daemon=True)
    t.start()

def send_p2p_email(target_ip, sender, receiver, subject, ciphertext, key_id, key_value, filename=None, file_bytes=None):
    """Alice runs this to beam data to Bob's IP."""
    try:
        # Prepare Payload
        payload = {
            "sender": sender,
            "receiver": receiver,
            "subject": subject,
            "body": ciphertext,
            "key_id": key_id,
            "key_value": key_value, # Sending key mostly for demo sync
            "filename": filename,
            "file_hex": file_bytes.hex() if file_bytes else None
        }
        
        # Connect & Send
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) # 5 second timeout
        s.connect((target_ip, PORT))
        s.sendall(json.dumps(payload).encode('utf-8'))
        s.close()
        return True, "Sent Successfully"
    except Exception as e:
        return False, str(e)