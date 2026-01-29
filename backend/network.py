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
            # 0.0.0.0 means "Listen to everyone on the Wi-Fi"
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
                    
                    if not data:
                        continue

                    # 2. Parse JSON
                    email_data = json.loads(data.decode('utf-8'))

                    # --- DEBUGGING LOGS (Check your Terminal for these!) ---
                    print("DEBUG: Checking Security Protocol...")
                    attack_on = False
                    if is_attack_active_callback:
                        attack_on = is_attack_active_callback()
                        print(f"DEBUG: Attack Button Status = {attack_on}")
                    else:
                        print("DEBUG: No attack callback linked!")
                    # -------------------------------------------------------

                    # --- SECURITY CHECK ---
                    # If the Red Button is ON, we destroy the message here.
                    if attack_on:
                        print("⚠️ ATTACK DETECTED! Message intercepted by Eve.")
                        print("🔥 DESTROYING MESSAGE. Nothing will be saved to DB.")
                        
                        # Tell the UI to show the Red Alert Popup
                        if update_callback:
                            update_callback(security_alert=True)
                            
                        client.close()
                        continue # STOP HERE. This prevents saving to the database.
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
                    print("✅ Email saved safely.")

                    # 5. Refresh UI (Normal Success)
                    if update_callback:
                        update_callback(security_alert=False)
                        
                except Exception as e:
                    print(f"❌ Network Error inside loop: {e}")
                finally:
                    client.close()
        except Exception as e:
            print(f"⚠️ Port Error: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()

def send_p2p_email(target_ip, sender, receiver, subject, ciphertext, key_id, key_value, filename=None, file_bytes=None):
    """Alice runs this to beam data to Bob's IP."""
    try:
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
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) 
        s.connect((target_ip, PORT))
        s.sendall(json.dumps(payload).encode('utf-8'))
        s.close()
        return True, "Sent Successfully"
    except Exception as e:
        return False, str(e)