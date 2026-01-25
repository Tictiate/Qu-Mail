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

## 🔮 Future Roadmap
- Integration with physical QKD hardware (ID Quantique / Toshiba).
- Expansion to **QuSuite** (Quantum Secure Chat & VoIP).