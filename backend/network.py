import socket
import json
import threading
import time
from . import db

# Port to listen on (Dynamic now)
PORT = 5005 

# 👇 THIS LINE IS THE FIX. MAKE SURE IT HAS BOTH ARGUMENTS.
def start_server(port, update_callback=None, is_attack_active_callback=None, on_interception_callback=None):
    """
    Bob runs this to listen.
    update_callback: Function to refresh UI.
    is_attack_active_callback: Function that returns True if attack is ON.
    on_interception_callback: Function to call when an interception is detected (Phase 2).
    """
    def listener():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 0.0.0.0 means "Listen to everyone on the Wi-Fi"
            server_socket.bind(('0.0.0.0', port)) 
            server_socket.listen(5)
            print(f"[*] Listening on Port {port}...")
            
            while True:
                client, addr = server_socket.accept()
                print(f"[+] Connection from {addr}")
                
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

                    # --- DEBUGGING LOGS ---
                    print("DEBUG: Checking Security Protocol...")
                    attack_on = False
                    # Check the callback you passed from main.py
                    if is_attack_active_callback:
                        attack_on = is_attack_active_callback()
                        print(f"DEBUG: Attack Button Status = {attack_on}")
                    else:
                        print("DEBUG: No attack callback linked!")
                    # ----------------------

                    # --- SECURITY CHECK ---
                    if attack_on:
                        print("[!] ATTACK DETECTED! Message intercepted by Eve.")
                        print("[!] DESTROYING MESSAGE. Nothing will be saved to DB.")
                        
                        # Phase 2: Call interception callback to alert receiver (Bob)
                        if on_interception_callback:
                            on_interception_callback(email_data.get('sender'), email_data.get('receiver'))
                        
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
                    print("OK: Email saved safely.")

                    # 5. Refresh UI (Normal Success)
                    if update_callback:
                        update_callback(security_alert=False)
                        
                except Exception as e:
                    print(f"ERR: Network Error inside loop: {e}")
                finally:
                    client.close()
        except Exception as e:
            print(f"ERR: Port Error: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()

def send_p2p_email(target_ip, target_port, sender, receiver, subject, ciphertext, key_id, key_value, filename=None, file_bytes=None):
    """Alice runs this to beam data to Bob's IP."""
    
    # 🔴 HACKER INTERCEPTION CHECK 🔴
    if db.is_hacker_listening():
        db.log_intercept(sender, receiver, ciphertext)
        db.set_hacker_listening(False) # Quantum state collapses!
        return False, "INTERCEPTED"

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
        s.connect((target_ip, target_port))
        s.sendall(json.dumps(payload).encode('utf-8'))
        s.close()
        return True, "Sent Successfully"
    except Exception as e:
        return False, str(e)

# --- Hacker state broadcast for cross-machine operation ---
HACKER_BROADCAST_PORT = 5009
HACKER_BROADCAST_MESSAGE = "QUMAIL_HACKER"
HACKER_STATE_QUERY = "QUMAIL_HACKER_QUERY"


def broadcast_hacker_state(enabled: bool):
    payload = f"{HACKER_BROADCAST_MESSAGE}:{1 if enabled else 0}"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1)
        sock.sendto(payload.encode('utf-8'), ('<broadcast>', HACKER_BROADCAST_PORT))
    except Exception as e:
        print(f"WARN: Could not broadcast hacker state: {e}")
    finally:
        sock.close()


def query_hacker_state():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)
        sock.sendto(HACKER_STATE_QUERY.encode('utf-8'), ('<broadcast>', HACKER_BROADCAST_PORT))
    except Exception as e:
        print(f"WARN: Could not query hacker state: {e}")
    finally:
        sock.close()


def start_hacker_state_listener():
    def listener():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", HACKER_BROADCAST_PORT))
        except Exception as e:
            print(f"WARN: Could not bind broadcast port {HACKER_BROADCAST_PORT}: {e}")
            return

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode('utf-8', errors='ignore')

                if msg == HACKER_STATE_QUERY:
                    # A new client is asking for state; respond if hacking is active
                    if db.is_hacker_listening():
                        sock.sendto(f"{HACKER_BROADCAST_MESSAGE}:1".encode('utf-8'), addr)
                    continue

                if not msg.startswith(HACKER_BROADCAST_MESSAGE):
                    continue

                _, state = msg.split(":", 1)
                hacking = state.strip() == "1"
                db.set_hacker_listening(hacking)
                print(f"DEBUG: Hacker broadcast from {addr}, active={hacking}")
            except Exception as e:
                print(f"WARN: Hacker listener error: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()


def start_hacker_state_publisher():
    def publisher():
        while True:
            if db.is_hacker_listening():
                broadcast_hacker_state(True)
            time.sleep(1)

    t = threading.Thread(target=publisher, daemon=True)
    t.start()