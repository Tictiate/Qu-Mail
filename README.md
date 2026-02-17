# ⚛️ QuMail - Quantum Secure Email Client

> **"Harvest Now, Decrypt Later" stops here.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Prototype-orange)]()

---

## 🧐 The Problem
We are currently living through a cybersecurity crisis. Hackers are stealing encrypted data today (Harvesting), waiting for Quantum Computers to break standard RSA/mathematical encryption tomorrow (Decrypting). Standard email protocols like TLS are mathematically vulnerable to future quantum attacks.

---

## 🛡️ The Solution: QuMail
QuMail is a **Quantum-Aided Email Client** that replaces "Hard Math" with "Physics."

It uses a decentralized **Peer-to-Peer (P2P)** architecture to simulate **Quantum Key Distribution (QKD)**, while also offering a hybrid layer for standard email clients like Gmail.

---

## ✨ Key Features

### 📡 Direct P2P Tunneling
Bypasses central servers entirely using raw TCP sockets for direct, localized secure communication.

### ⚛️ Quantum "Observer Effect" Simulation
- **Normal Mode:** Secure transmission of encrypted messages.  
- **Attack Mode:** If a hacker (Man-in-the-Middle) attempts to intercept the stream, the system detects the spike in QBER (Quantum Bit Error Rate).  
- **Self-Destruct:** The message is immediately destroyed in transit. The hacker gets nothing.

### 📧 Hybrid Mode (Gmail Integration)
Send Quantum-Encrypted emails over standard SMTP (Gmail). Hackers on the network only see quantum noise.

### 🔓 External Decryption Tool
A built-in tool allowing receivers using standard web browsers to paste their Ciphertext and Quantum Key to reveal the hidden message.

### 🔐 Ephemeral Keys
Keys are generated for a single transaction (Perfect Forward Secrecy) and burned immediately.

---

## 🛠️ Tech Stack
- **Language:** Python 3  
- **GUI:** PyQt6 (Modern Dark Theme)  
- **Networking:** Python `socket` & `threading` (Custom P2P Protocol) + `smtplib` (Gmail)  
- **Cryptography:** `cryptography` library (AES-256 via Fernet)  
- **Database:** SQLite (Local storage, zero-cloud architecture)

---

## 🚀 How to Run the App

### 1️⃣ Install Dependencies
We keep our environment extremely lightweight. Run:

```bash
pip install PyQt6 cryptography
```

### 2️⃣ Start the App

```bash
python3 main.py
```

> **Note:** Use `python` instead of `python3` if you are on Windows.

---

## 🎬 How to Demo the Features

### Demo 1 — The "Hacker Simulation" (P2P Mode)
**Requires two computers on the same Wi-Fi network.**

**Laptop B (Receiver):** Click the red **🔴 SIMULATE ATTACK** button to act as an eavesdropper.  

**Laptop A (Sender):**
1. Draft a message  
2. Select **📡 Quantum Direct (P2P)**  
3. Enter Laptop B's IP address  
4. Click Send  

**Result:**  
The connection detects intrusion, drops the socket, and triggers a **SECURITY INTERVENTION** alert. The data is destroyed.

---

### Demo 2 — The "Hybrid Web" (Gmail Mode)

**Sender:**  
Select **📧 Standard Gmail**, enter App Password, send email.

**Hacker View:**  
The email travels through Google servers. Anyone intercepting sees only:

```
gAAAAAB...
```

**Receiver:**  
1. Open Gmail in browser  
2. Copy Ciphertext + Key  

**Decryption:**  
Open QuMail → **🔓 Decrypt Tool tab** → Paste data → Message revealed securely.

---

## 👥 The Team
Built by **Team ARIA** for Hackathon demonstration purposes.
