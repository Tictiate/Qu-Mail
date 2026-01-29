import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLabel, 
                             QPushButton, QSplitter, QLineEdit, QMessageBox, 
                             QStackedWidget, QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from backend import db, crypto, network

class QuMailClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuMail - Quantum Secure Client")
        self.resize(1200, 700)
        
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
        self.nav_list.addItems(["📥 Inbox", "✍️ Compose", "📤 Sent"])
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
        status_layout