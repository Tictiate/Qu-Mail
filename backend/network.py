import socket
import json
import threading
from . import db

# Port to listen on (Arbitrary, but must match on both PCs)
PORT = 5005 

def start_server(update_callback=None, is_attack_active_callback=None):
    """
    Bob runs this to listen.
    update_callback: Function to refresh UI.
    is_attack_active_callback: Function that returns True if attack is ON.
    """
    def listener():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind(('0.0.0.0', PORT)) 
            server_socket.listen(5)
            print(f"👂 Listening on Port {PORT}...")
            
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

                    # --- SECURITY CHECK (NEW) ---
                    # Before saving, check if the "Attack" button is pressed
                    if is_attack_active_callback and is_attack_active_callback():
                        print("⚠️ ATTACK DETECTED! Message intercepted by Eve.")
                        print("🔥 DESTROYING MESSAGE to protect secrets.")
                        
                        # Trigger the "Destroyed" alert in the UI
                        if update_callback:
                            update_callback(security_alert=True)
                            
                        client.close()
                        continue # STOP HERE. Do not save to DB.
                    # -----------------------------
                    
                    # 3. Handle File Blob
                    file_blob = None
                    if email_data.get('file_hex'):
                        file_blob = bytes.fromhex(email_data['file_hex'])
                    
                    # 4. Save to DB (Only happens if NO attack)
                    db.save_email(
                        sender=email_data['sender'],
                        receiver=email_data['receiver'],
                        subject=email_data['subject'],
                        ciphertext=email_data['body'],
                        key_id=email_data['key_id'],
                        filename=email_data.get('filename'),
                        file_data=file_blob
                    )
                    
                    db.store_key(email_data['key_id'], email_data['key_value'])

                    # 5. Refresh UI (Normal Success)
                    if update_callback:
                        update_callback(security_alert=False)
                        
                except Exception as e:
                    print(f"❌ Network Error: {e}")
                finally:
                    client.close()
        except Exception as e:
            print(f"⚠️ Port Error: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()