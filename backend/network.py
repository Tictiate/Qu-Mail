import socket
import json
import threading
from . import db

# Port to listen on (Arbitrary, but must match on both PCs)
PORT = 5005 

def start_server(update_callback=None):
    """
    Bob runs this to listen for incoming emails.
    update_callback: Optional function to refresh UI when mail arrives.
    """
    def listener():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 0.0.0.0 means "Listen to everyone on the Wi-Fi"
        try:
            server_socket.bind(('0.0.0.0', PORT)) 
            server_socket.listen(5)
            print(f"👂 Listening for Quantum Mail on Port {PORT}...")
            
            while True:
                client, addr = server_socket.accept()
                print(f"📡 Connection from {addr}")
                
                try:
                    # 1. Receive Data
                    data = b""
                    while True:
                        packet = client.recv(4096)
                        if not packet: break
                        data += packet
                    
                    # 2. Parse JSON
                    email_data = json.loads(data.decode('utf-8'))
                    
                    # 3. Handle File Blob (Convert hex back to bytes)
                    file_blob = None
                    if email_data.get('file_hex'):
                        file_blob = bytes.fromhex(email_data['file_hex'])
                    
                    # 4. Save to Local DB
                    db.save_email(
                        sender=email_data['sender'],
                        receiver=email_data['receiver'],
                        subject=email_data['subject'],
                        ciphertext=email_data['body'],
                        key_id=email_data['key_id'],
                        filename=email_data.get('filename'),
                        file_data=file_blob
                    )
                    
                    # 5. Save the Key (Sync)
                    db.store_key(email_data['key_id'], email_data['key_value'])
                    print("✅ Email received and saved to DB.")

                    # 6. Refresh UI if callback is provided
                    if update_callback:
                        update_callback()
                        
                except Exception as e:
                    print(f"❌ Network Error: {e}")
                finally:
                    client.close()
        except Exception as e:
            print(f"⚠️ Could not bind port {PORT}: {e}")

    # Run listener in background
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
            "key_value": key_value,
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