import socket
import json
import threading
import time
from . import db
from . import crypto

# Port to listen on (Dynamic now)
PORT = 5005 

# Transport plugin abstraction
class TransportPlugin:
    def send_email(self, target_ip, target_port, payload):
        raise NotImplementedError()

    def perform_handshake(self, target_ip, target_port, sender, secret):
        raise NotImplementedError()


class TCPTransportPlugin(TransportPlugin):
    def send_email(self, target_ip, target_port, payload):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target_ip, target_port))
        s.sendall(json.dumps(payload).encode('utf-8'))
        s.close()

    def perform_handshake(self, target_ip, target_port, sender, secret):
        nonce = str(int(time.time() * 1000))
        token = crypto.generate_handshake_token(secret, nonce)
        hs_payload = {"type": "handshake", "sender": sender, "nonce": nonce, "token": token}

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target_ip, target_port))
        s.sendall(json.dumps(hs_payload).encode('utf-8'))

        try:
            reply = s.recv(1024)
            s.close()
            if not reply: return False, "No handshake response"
            resp = json.loads(reply.decode('utf-8'))
            return resp.get("status") == "ok", resp.get("message", "")
        except Exception as e:
            s.close()
            return False, str(e)


default_transport = TCPTransportPlugin()

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
                    # 1. Receive Data with timeout to prevent hanging
                    client.settimeout(2)  # 2-second timeout to avoid EOF deadlock
                    data = b""
                    try:
                        # Try to receive data (will timeout if client doesn't send anything)
                        data = client.recv(4096)
                    except socket.timeout:
                        # Timeout is OK, client might have sent everything in one packet
                        pass
                    
                    if not data:
                        client.close()
                        continue

                    # 2. Parse JSON
                    email_data = json.loads(data.decode('utf-8'))

                    # Handshake handling (authenticated QKD)
                    if email_data.get('type') == 'handshake':
                        sender = email_data.get('sender')
                        nonce = email_data.get('nonce')
                        token = email_data.get('token')
                        if sender and nonce and token:
                            # Validate handshake token with seed-based secret using sender and nonce
                            # For this prototype we assume secret = sender email itself (in real world use shared secret)
                            if crypto.validate_handshake_token(sender, nonce, token):
                                response = json.dumps({'status': 'ok', 'message': 'handshake confirmed'})
                                client.sendall(response.encode('utf-8'))
                                db.log_channel_event('handshake', f'{sender} -> {sender}', qber=None)
                            else:
                                response = json.dumps({'status': 'failed', 'message': 'invalid token'})
                                client.sendall(response.encode('utf-8'))
                                db.log_channel_event('handshake_failed', f'sender={sender}', qber=None)
                        else:
                            response = json.dumps({'status': 'failed', 'message': 'missing handshake fields'})
                            client.sendall(response.encode('utf-8'))
                        client.close()
                        continue

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

def send_p2p_email(target_ip, target_port, sender, receiver, subject, ciphertext, key_id, key_value, filename=None, file_bytes=None, transport=None):
    """Alice runs this to beam data to Bob's IP."""
    if transport is None:
        transport = default_transport

    # 🔴 HACKER INTERCEPTION CHECK 🔴
    if is_hacker_active() or db.is_hacker_listening():
        db.log_intercept(sender, receiver, ciphertext)
        db.log_channel_event("interception", f"sender={sender};receiver={receiver}", qber=999)
        return False, "INTERCEPTED"

    # Phase 2: Authenticated QKD handshake (identity-used for demonstration)
    ok, msg = transport.perform_handshake(target_ip, target_port, sender, sender)
    if not ok:
        db.log_channel_event("handshake_failed", msg)
        return False, f"Handshake failed: {msg}"

    try:
        payload = {
            "type": "email",
            "sender": sender,
            "receiver": receiver,
            "subject": subject,
            "body": ciphertext,
            "key_id": key_id,
            "key_value": key_value,
            "filename": filename,
            "file_hex": file_bytes.hex() if file_bytes else None
        }

        transport.send_email(target_ip, target_port, payload)
        db.log_channel_event("send", f"sender={sender};receiver={receiver}")
        return True, "Sent Successfully"
    except Exception as e:
        db.log_channel_event("send_failed", str(e))
        return False, str(e)

# --- Hacker state broadcast for cross-machine operation ---
HACKER_BROADCAST_PORT = 5009
HACKER_BROADCAST_MESSAGE = "QUMAIL_HACKER"
HACKER_STATE_QUERY = "QUMAIL_HACKER_QUERY"
HACKER_EXPIRATION_SECONDS = 5

hacker_last_seen_ts = 0


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

        global hacker_last_seen_ts
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode('utf-8', errors='ignore')

                if msg == HACKER_STATE_QUERY:
                    # A new client asks for current state; answer only when attacker known active
                    if db.is_hacker_listening():
                        sock.sendto(f"{HACKER_BROADCAST_MESSAGE}:1".encode('utf-8'), addr)
                    continue

                if not msg.startswith(HACKER_BROADCAST_MESSAGE):
                    continue

                _, state = msg.split(":", 1)
                hacking = state.strip() == "1"
                if hacking:
                    set_hacker_last_seen()
                    db.set_hacker_listening(True)
                else:
                    # Keep the attack lingering briefly; avoid transient 0->1 flaps
                    db.set_hacker_listening(False)
                print(f"DEBUG: Hacker broadcast from {addr}, active={hacking}")
            except Exception as e:
                print(f"WARN: Hacker listener error: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()


def start_hacker_state_publisher():
    def publisher():
        while True:
            if db.is_hacker_listening():
                set_hacker_last_seen()
                broadcast_hacker_state(True)
            time.sleep(1)

    t = threading.Thread(target=publisher, daemon=True)
    t.start()


def set_hacker_last_seen():
    global hacker_last_seen_ts
    hacker_last_seen_ts = time.time()


def is_hacker_active():
    global hacker_last_seen_ts
    # Ensure DB state expires if no recent broadcast (except initial local hacker state)
    if db.is_hacker_listening():
        if hacker_last_seen_ts == 0:
            return True
        if time.time() - hacker_last_seen_ts > HACKER_EXPIRATION_SECONDS:
            db.set_hacker_listening(False)
            return False
        return True
    return False


def start_hacker_state_query_loop():
    def query_loop():
        while True:
            query_hacker_state()
            time.sleep(2)

    t = threading.Thread(target=query_loop, daemon=True)
    t.start()