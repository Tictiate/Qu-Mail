# 🛡️ QuMail: Quantum-Secure Email Client

**QuMail** is a post-quantum cryptographic email client that integrates **Quantum Key Distribution (QKD)** with standard email protocols (SMTP/IMAP). It is designed to protect communication against the "Harvest Now, Decrypt Later" threat posed by future quantum computers.

## 🚀 Features
- **Quantum Key Simulation:** Implements a mock **ETSI GS QKD 014** REST API for key delivery.
- **Multi-Level Security:**
  - **Level 1:** One-Time Pad (Information-Theoretic Security).
  - **Level 2:** AES-256 seeded with Quantum Keys.
- **Interoperability:** Works on top of existing email providers (Gmail, Yahoo) without infrastructure changes.
- **Zero-Knowledge Architecture:** The email provider never sees the decryption keys.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Python)
- **Encryption:** Cryptography (Fernet/AES)
- **Protocol:** ETSI GS QKD 014 (Simulated)
- **Transport:** Standard SMTP/TLS

## ⚡ Quick Start
1. Clone the repo
2. Install dependencies: `pip install streamlit cryptography`
3. Run the app: `streamlit run app.py`

## 📐 How To Test
1. Go to `qumail-demo.streamlit.app`
2. In the compose tab, put in a test email for the recipient (eg. test@test.com) and type in any message. (you can keep the sender e-mail and password blank)
3. Click on "Encrypt & Send"
4. It will say "Failed to send email" BUT look at the yellow warning box below it.
5. Inside that box, you will see the KEY_ID (e.g., 8F2A) and the long gibberish text (the cipher_text). Copy them.
6. Go to Tab 2. Paste the Key ID and the gibberish text. Click Decrypt.
7. You should see your message appear with balloons.

## 🔮 Future Roadmap
- Integration with physical QKD hardware (ID Quantique / Toshiba).
- Expansion to **QuSuite** (Quantum Secure Chat & VoIP).