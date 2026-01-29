import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLabel, 
                             QPushButton, QSplitter, QLineEdit, QMessageBox, 
                             QStackedWidget, QComboBox, QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from backend import db, crypto, network  # Added network import

class QuMailClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Quantum Secure Client")
        self.resize(1200, 700)
        
        # --- 1. THE LAYOUT ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANE (Navigation) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("👤 Current User:"))
        self.user_combo = QComboBox()
        self.user_combo.addItems(["alice@quantum.com", "bob@quantum.com", "eve@hacker.net"])
        self.user_combo.currentTextChanged.connect(self.change_user)
        left_layout.addWidget(self.user_combo)
        
        self.nav_list = QListWidget()
        self.nav_list.addItems(["📥 Inbox", "✍️ Compose", "📤 Sent"])
        self.nav_list.currentRowChanged.connect(self.switch_mode)
        left_layout.addWidget(self.nav_list)

        # BUTTONS & DASHBOARD
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
        
        # NEW: IP Input
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("Target IP (e.g., 192.168.1.5)")
        self.input_ip.setStyleSheet("border: 1px solid #0e639c;")
        
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
        
        compose_layout.addWidget(QLabel("Target IP Address (Bob's PC):"))
        compose_layout.addWidget(self.input_ip)
        compose_layout.addWidget(self.input_to)
        compose_layout.addWidget(self.input_subject)
        compose_layout.addWidget(self.input_body)
        compose_layout.addLayout(attach_layout)
        compose_layout.addWidget(self.btn_send)
        
        self.right_pane.addWidget(self.read_view)
        self.right_pane.addWidget(self.compose_view)
        
        # SPLITTER SETUP
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.email_list)
        self.splitter.addWidget(self.right_pane)
        self.splitter.setSizes([250, 300, 650])
        main_layout.addWidget(self.splitter)
        
        # INIT
        db.init_db()
        network.start_server() # Start Listening!
        self.current_user = "alice@quantum.com"
        self.current_folder = "inbox"
        self.current_attachment_path = None
        self.apply_dark_theme()
        self.load_emails()

    def send_email(self):
        target_ip = self.input_ip.text().strip()
        receiver = self.input_to.text().strip()
        subject = self.input_subject.text().strip()
        body = self.input_body.toPlainText().strip()
        
        if not target_ip or not receiver:
            QMessageBox.warning(self, "Missing Info", "Please enter Target IP and Receiver!")
            return

        try:
            # 1. Encrypt
            key_id, key = crypto.generate_quantum_key()
            encrypted_body = crypto.encrypt_content(body, key)
            
            # File
            filename = None
            encrypted_file = None
            raw_bytes = None
            if self.current_attachment_path:
                filename = self.current_attachment_path.split("/")[-1]
                with open(self.current_attachment_path, "rb") as f:
                    raw_bytes = f.read()
                encrypted_file = crypto.encrypt_file_bytes(raw_bytes, key)

            # 2. Save Locally (Sent Box)
            db.save_email(self.current_user, receiver, subject, encrypted_body, key_id, filename, encrypted_file)

            # 3. Send over Network
            success, msg = network.send_p2p_email(
                target_ip, self.current_user, receiver, subject, 
                encrypted_body, key_id, key.decode(), filename, encrypted_file
            )

            if success:
                QMessageBox.information(self, "Sent", f"Message Beamed to {target_ip}!")
                self.input_body.clear()
                self.nav_list.setCurrentRow(2) 
            else:
                QMessageBox.critical(self, "Failed", f"Connection Error:\n{msg}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # --- KEEP YOUR EXISTING HELPER FUNCTIONS BELOW ---
    # (Copy-paste the update_status, toggle_attack, switch_mode, change_user, 
    #  load_emails, open_email, select_file, decrypt, download, apply_dark_theme 
    #  from the previous response here. They have not changed.)
    
    def update_status(self):
        noise = random.uniform(0.1, 1.5)
        if self.current_user == "eve@hacker.net": 
            noise = random.uniform(25.0, 55.0)
            self.bar_qber.setStyleSheet("QProgressBar::chunk { background-color: #ff3333; }")
        else:
            self.bar_qber.setStyleSheet("QProgressBar::chunk { background-color: #00ff00; }")
        self.bar_qber.setValue(int(noise))
        self.lbl_qber.setText(f"QBER: {noise:.2f}%")

    def toggle_attack(self):
        if self.btn_hack.isChecked():
            self.btn_hack.setText("⚠️ ATTACK ACTIVE")
            self.current_user = "eve@hacker.net"
            QMessageBox.warning(self, "INTERCEPTION STARTED", "Quantum Channel Compromised!")
        else:
            self.btn_hack.setText("🔴 SIMULATE ATTACK")
            self.current_user = "alice@quantum.com"

    def switch_mode(self, index):
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

    def change_user(self, new_user):
        self.current_user = new_user
        self.nav_list.setCurrentRow(0)

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
            QLineEdit, QTextEdit, QComboBox { background-color: #3c3c3c; color: white; border: 1px solid #555; padding: 5px; }
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