import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLabel, 
                             QPushButton, QSplitter, QLineEdit, QMessageBox, 
                             QStackedWidget, QFileDialog, QProgressBar, QRadioButton, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from backend import db, crypto, network, smtp_client

class QuMailClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Quantum Secure Client")
        self.resize(1200, 750)
        
        # --- LAYOUT SETUP ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANE ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("👤 My Identity:"))
        self.input_identity = QLineEdit()
        self.input_identity.setText("alice@quantum.com") 
        self.input_identity.textChanged.connect(self.update_identity)
        left_layout.addWidget(self.input_identity)
        
        self.nav_list = QListWidget()
        # Added "Decrypt Tool" to the list
        self.nav_list.addItems(["📥 Inbox", "✍️ Compose", "📤 Sent", "🔓 Decrypt Tool"])
        self.nav_list.currentRowChanged.connect(self.switch_mode)
        left_layout.addWidget(self.nav_list)

        # HACKER BUTTON
        self.btn_hack = QPushButton("🔴 SIMULATE ATTACK")
        self.btn_hack.setCheckable(True)
        self.btn_hack.setStyleSheet("background-color: #550000; color: white; border: 1px solid red;")
        self.btn_hack.clicked.connect(self.toggle_attack)
        left_layout.addWidget(self.btn_hack)

        # DASHBOARD
        status_widget = QWidget()
        status_widget.setStyleSheet("background-color: #2d2d2d; border-radius: 5px; padding: 5px; margin-top: 10px;")
        status_layout = QVBoxLayout(status_widget)
        status_layout.addWidget(QLabel("⚛️ QUANTUM LINK STATUS"))
        self.lbl_qber = QLabel("QBER: 0.00%")
        status_layout.addWidget(self.lbl_qber)
        self.bar_qber = QProgressBar()
        self.bar_qber.setRange(0, 100)
        status_layout.addWidget(self.bar_qber)
        left_layout.addWidget(status_widget)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

        # --- MIDDLE PANE ---
        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.open_email)
        
        # --- RIGHT PANE ---
        self.right_pane = QStackedWidget()
        
        # VIEW 0: READ
        self.read_view = QWidget()
        read_layout = QVBoxLayout(self.read_view)
        self.lbl_subject = QLabel("<h2>Select an email</h2>")
        self.lbl_sender = QLabel("From: -")
        self.txt_body = QTextEdit()
        self.txt_body.setReadOnly(True)
        self.btn_decrypt = QPushButton("🔓 Decrypt with Quantum Key")
        self.btn_decrypt.clicked.connect(self.decrypt_current_email)
        self.btn_decrypt.hide()
        self.btn_download = QPushButton("💾 Download Attachment")
        self.btn_download.clicked.connect(self.download_attachment)
        self.btn_download.hide()
        read_layout.addWidget(self.lbl_subject)
        read_layout.addWidget(self.lbl_sender)
        read_layout.addWidget(self.txt_body)
        read_layout.addWidget(self.btn_decrypt)
        read_layout.addWidget(self.btn_download)
        
        # VIEW 1: COMPOSE
        self.compose_view = QWidget()
        compose_layout = QVBoxLayout(self.compose_view)
        
        mode_layout = QHBoxLayout()
        self.radio_p2p = QRadioButton("📡 Quantum Direct (P2P)")
        self.radio_gmail = QRadioButton("📧 Standard Gmail")
        self.radio_p2p.setChecked(True)
        self.radio_p2p.toggled.connect(self.toggle_compose_mode)
        mode_layout.addWidget(self.radio_p2p)
        mode_layout.addWidget(self.radio_gmail)
        mode_layout.addStretch()
        compose_layout.addLayout(mode_layout)

        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("Target IP (e.g., 192.168.1.5)")
        self.input_ip.setStyleSheet("border: 1px solid #0e639c;")
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Gmail App Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.hide() 
        
        self.input_to = QLineEdit()
        self.input_to.setPlaceholderText("To: bob@quantum.com")
        self.input_subject = QLineEdit()
        self.input_subject.setPlaceholderText("Subject")
        self.input_body = QTextEdit()
        
        attach_layout = QHBoxLayout()
        self.btn_attach = QPushButton("📎 Attach File")
        self.btn_attach.clicked.connect(self.select_file)
        self.lbl_filename = QLabel("No file selected")
        attach_layout.addWidget(self.btn_attach)
        attach_layout.addWidget(self.lbl_filename)
        attach_layout.addStretch()
        
        self.btn_send = QPushButton("🚀 Beam to Target PC")
        self.btn_send.clicked.connect(self.send_email)
        
        compose_layout.addWidget(self.input_ip)
        compose_layout.addWidget(self.input_password)
        compose_layout.addWidget(self.input_to)
        compose_layout.addWidget(self.input_subject)
        compose_layout.addWidget(self.input_body)
        compose_layout.addLayout(attach_layout)
        compose_layout.addWidget(self.btn_send)
        
        # VIEW 2: MANUAL DECRYPT TOOL (NEW!)
        self.decrypt_tool_view = QWidget()
        dt_layout = QVBoxLayout(self.decrypt_tool_view)
        
        dt_layout.addWidget(QLabel("<h2>🔓 External Decryption Tool</h2>"))
        dt_layout.addWidget(QLabel("Paste the encrypted text and key from your Gmail here."))
        
        self.input_dt_cipher = QTextEdit()
        self.input_dt_cipher.setPlaceholderText("Paste Ciphertext (The garbage text) here...")
        
        self.input_dt_key = QLineEdit()
        self.input_dt_key.setPlaceholderText("Paste Quantum Key here...")
        
        self.btn_manual_decrypt = QPushButton("🔓 Decrypt Message")
        self.btn_manual_decrypt.clicked.connect(self.run_manual_decryption)
        self.btn_manual_decrypt.setStyleSheet("background-color: #0e639c; height: 40px; font-weight: bold;")
        
        self.output_dt_plain = QTextEdit()
        self.output_dt_plain.setPlaceholderText("Decrypted message will appear here...")
        self.output_dt_plain.setReadOnly(True)
        self.output_dt_plain.setStyleSheet("border: 1px solid #00ff00; color: #00ff00;")
        
        dt_layout.addWidget(QLabel("1. Ciphertext:"))
        dt_layout.addWidget(self.input_dt_cipher)
        dt_layout.addWidget(QLabel("2. Quantum Key:"))
        dt_layout.addWidget(self.input_dt_key)
        dt_layout.addWidget(self.btn_manual_decrypt)
        dt_layout.addWidget(QLabel("3. Result:"))
        dt_layout.addWidget(self.output_dt_plain)

        # Add views to Stack
        self.right_pane.addWidget(self.read_view)        # Index 0
        self.right_pane.addWidget(self.compose_view)     # Index 1
        self.right_pane.addWidget(self.decrypt_tool_view) # Index 2
        
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.email_list)
        self.splitter.addWidget(self.right_pane)
        self.splitter.setSizes([250, 300, 650])
        main_layout.addWidget(self.splitter)
        
        # --- INITIALIZATION ---
        db.init_db()
        network.start_server(self.trigger_refresh, self.check_attack_status)
        
        self.current_user = self.input_identity.text()
        self.current_folder = "inbox"
        self.current_attachment_path = None
        self.apply_dark_theme()
        self.load_emails()

    # --- LOGIC ---

    def run_manual_decryption(self):
        """Decrypts text pasted from external sources (Gmail)"""
        # 1. Get Text
        raw_cipher = self.input_dt_cipher.toPlainText()
        raw_key = self.input_dt_key.text()
        
        # 2. Aggressive Cleaning (The Fix)
        # Gmail adds newlines every 70 characters. We must remove them.
        ciphertext = raw_cipher.replace(" ", "").replace("\n", "").replace("\r", "").strip()
        key_str = raw_key.strip()
        
        if not ciphertext or not key_str:
            QMessageBox.warning(self, "Missing Data", "Please paste both the Ciphertext and the Key!")
            return
            
        # 3. Debug Print (Look at your Terminal if it fails!)
        print(f"DEBUG: Attempting decrypt with Key: {key_str[:10]}...")
        
        # 4. Try Decrypt
        plaintext = crypto.decrypt_content(ciphertext, key_str)
        
        if "❌" in plaintext:
            # Show the actual python error in the box so we know WHY it failed
            self.output_dt_plain.setText(f"FAILED. System Error:\n{plaintext}")
            self.output_dt_plain.setStyleSheet("border: 1px solid red; color: red;")
        else:
            self.output_dt_plain.setText(plaintext)
            self.output_dt_plain.setStyleSheet("border: 1px solid #00ff00; color: #00ff00;")
            QMessageBox.information(self, "Success", "Message Decrypted Successfully!")

    def toggle_compose_mode(self):
        if self.radio_p2p.isChecked():
            self.input_ip.show()
            self.input_password.hide()
            self.btn_send.setText("🚀 Beam to Target PC")
            self.input_ip.setPlaceholderText("Target IP (e.g., 192.168.1.5)")
        else:
            self.input_ip.hide()
            self.input_password.show()
            self.btn_send.setText("✉️ Send Encrypted Gmail")

    def check_attack_status(self):
        return self.btn_hack.isChecked()

    def trigger_refresh(self, security_alert=False):
        if security_alert:
            QTimer.singleShot(0, self.show_destruction_alert)
        else:
            print("📩 New Mail! Refreshing UI...")
            QTimer.singleShot(0, self.load_emails)

    def show_destruction_alert(self):
        QMessageBox.critical(self, "🛑 SECURITY INTERVENTION", 
                             "Eavesdropper (Eve) Detected!\n\n"
                             "The message was DESTROYED in transit.")

    def update_identity(self):
        self.current_user = self.input_identity.text()
        self.load_emails()

    def send_email(self):
        receiver = self.input_to.text().strip()
        subject = self.input_subject.text().strip()
        body = self.input_body.toPlainText().strip()
        
        # --- 1. ENCRYPTION ---
        key_id, key = crypto.generate_quantum_key()
        encrypted_body = crypto.encrypt_content(body, key)
        
        # Save Key locally for the sender
        db.store_key(key_id, key.decode()) 
        
        encrypted_file = None
        filename = None
        if self.current_attachment_path:
            filename = self.current_attachment_path.split("/")[-1]
            with open(self.current_attachment_path, "rb") as f:
                encrypted_file = crypto.encrypt_file_bytes(f.read(), key)

        # MODE 1: P2P
        if self.radio_p2p.isChecked():
            target_ip = self.input_ip.text().strip()
            if not target_ip or not receiver:
                QMessageBox.warning(self, "Missing Info", "Please enter Target IP and Receiver!")
                return
            
            try:
                db.save_email(self.current_user, receiver, subject, encrypted_body, key_id, filename, encrypted_file)
                success, msg = network.send_p2p_email(target_ip, self.current_user, receiver, subject, encrypted_body, key_id, key.decode(), filename, encrypted_file)

                if success:
                    QMessageBox.information(self, "Sent", f"Message Beamed to {target_ip}!")
                    self.input_body.clear()
                    self.nav_list.setCurrentRow(2) 
                else:
                    QMessageBox.critical(self, "Failed", f"Connection Error:\n{msg}")

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
        
        # MODE 2: GMAIL
        else:
            sender_password = self.input_password.text().strip()
            if not sender_password:
                QMessageBox.warning(self, "Missing Password", "Please enter Gmail App Password!")
                return

            email_content = f"""
🔒 QUANTUM SECURE MESSAGE 🔒
------------------------------------------------
This email was encrypted using the QuMail Protocol.

CIPHERTEXT:
{encrypted_body}

------------------------------------------------
QUANTUM KEY (Copy this):
{key.decode()}
            """

            success, msg = smtp_client.send_gmail(
                self.current_user, 
                sender_password, 
                receiver, 
                subject, 
                email_content, 
                self.current_attachment_path 
            )
            
            if success:
                QMessageBox.information(self, "Success", "Encrypted Email sent via Gmail!")
                db.save_email(self.current_user, receiver, subject, encrypted_body, key_id, filename, encrypted_file)
                self.nav_list.setCurrentRow(2)
            else:
                QMessageBox.critical(self, "Gmail Error", f"Could not send:\n{msg}")

    def update_status(self):
        noise = random.uniform(0.1, 1.5)
        if self.btn_hack.isChecked(): 
            noise = random.uniform(25.0, 55.0)
            self.bar_qber.setStyleSheet("QProgressBar::chunk { background-color: #ff3333; }")
        else:
            self.bar_qber.setStyleSheet("QProgressBar::chunk { background-color: #00ff00; }")
        self.bar_qber.setValue(int(noise))
        self.lbl_qber.setText(f"QBER: {noise:.2f}%")

    def toggle_attack(self):
        if self.btn_hack.isChecked():
            self.btn_hack.setText("⚠️ ATTACK ACTIVE")
            QMessageBox.warning(self, "INTERCEPTION STARTED", "Channel Compromised!")
        else:
            self.btn_hack.setText("🔴 SIMULATE ATTACK")

    def switch_mode(self, index):
        # 0=Inbox, 1=Compose, 2=Sent, 3=Decrypt Tool
        if index == 0:
            self.current_folder = "inbox"
            self.right_pane.setCurrentIndex(0)
            self.load_emails()
        elif index == 1:
            self.right_pane.setCurrentIndex(1)
        elif index == 2:
            self.current_folder = "sent"
            self.right_pane.setCurrentIndex(0)
            self.load_emails()
        elif index == 3:
            # Show the Decrypt Tool
            self.right_pane.setCurrentIndex(2)

    def load_emails(self):
        self.email_list.clear()
        if self.current_folder == "inbox":
            emails = db.get_inbox(self.current_user)
            icon = "📥"
            prefix = "From:"
        else:
            emails = db.get_sent_box(self.current_user)
            icon = "📤"
            prefix = "To:"
        for email in emails:
            display_name = email[1] if self.current_folder == "inbox" else email[2]
            self.email_list.addItem(f"{icon} {email[3]}\n{prefix} {display_name}")
            item = self.email_list.item(self.email_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, email)

    def open_email(self, item):
        email_data = item.data(Qt.ItemDataRole.UserRole)
        self.selected_email_data = email_data
        self.right_pane.setCurrentIndex(0)
        self.lbl_subject.setText(f"<h2>{email_data[3]}</h2>")
        self.lbl_sender.setText(f"User: {email_data[1]} | Time: {email_data[6]}")
        self.txt_body.setText(email_data[4])
        self.btn_decrypt.show()
        if len(email_data) > 7 and email_data[7]: 
            self.btn_download.setText(f"💾 Download {email_data[7]}")
            self.btn_download.show()
        else:
            self.btn_download.hide()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if file_path:
            self.current_attachment_path = file_path
            self.lbl_filename.setText(f"📎 {file_path.split('/')[-1]}")

    def decrypt_current_email(self):
        if self.selected_email_data:
            key_id = self.selected_email_data[5]
            ciphertext = self.selected_email_data[4]
            plaintext = crypto.decrypt_content(ciphertext, key_id)
            if "❌" in plaintext: QMessageBox.critical(self, "Security Alert", plaintext)
            else: 
                self.txt_body.setText(plaintext)
                QMessageBox.information(self, "Success", f"Decrypted with Key: {key_id}")

    def download_attachment(self):
        if not self.selected_email_data: return
        filename = self.selected_email_data[7]
        encrypted_blob = self.selected_email_data[8]
        key_id = self.selected_email_data[5]
        decrypted_bytes = crypto.decrypt_file_bytes(encrypted_blob, key_id)
        if not decrypted_bytes: return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if save_path:
            with open(save_path, "wb") as f: f.write(decrypted_bytes)
            QMessageBox.information(self, "Success", "File Saved!")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: white; }
            QListWidget { background-color: #252526; color: #cccccc; border: none; font-size: 14px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #37373d; color: white; }
            QLineEdit, QTextEdit { background-color: #3c3c3c; color: white; border: 1px solid #555; padding: 5px; }
            QPushButton { background-color: #0e639c; color: white; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #1177bb; }
            QLabel { color: #cccccc; }
            QSplitter::handle { background-color: #444; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuMailClient()
    window.show()
    sys.exit(app.exec())