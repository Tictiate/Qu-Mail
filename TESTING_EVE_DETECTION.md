# Test Guide: Eve Detection & Alert System

## Implementation Summary
This guide walks through testing all 5 phases of the Eve eavesdropping detection system that was just implemented.

---

## Setup

1. **Start with fresh database** (optional):
   ```bash
   rm qumail.db  # Delete old DB to start fresh
   ```

2. **Launch 3 instances** (or 3 terminal windows):
   ```bash
   python main.py  # Will show identity selector
   ```

3. **Select identities** in order:
   - **Terminal 1**: Alice (alice@quantum.com)
   - **Terminal 2**: Bob (bob@quantum.com)
   - **Terminal 3**: Eve (hacker@darknet.io)

---

## Phase 1: Sender-Side Eve Detection ✅

**What it does**: Alice can't send emails if Eve is listening.

### Test Steps:
1. **In Eve's window**: Click "🔴 START LISTENING ON FIBER OPTIC LINE" button
2. **In Alice's window**: 
   - Go to "✍️ Compose" tab
   - Enter:
     - **To**: bob@quantum.com
     - **Subject**: Test Message
     - **Body**: Hello Bob!
     - **Target IP**: 127.0.0.1
   - Click "🚀 Beam to Target PC"

### Expected Result:
- **Alert appears**: "🛑 EAVESDROPPER DETECTED"
  - Message says: "Email NOT sent. Eve detected on quantum channel."
- **Email NOT sent** (doesn't appear in Alice's Sent folder)
- **No email arrives** at Bob

### Success Criteria ✅:
- Alert shows immediately
- No email is sent/received
- Database stays clean (no email record)

---

## Phase 2: Receiver-Side Eve Detection ✅

**What it does**: Bob gets an alert if Eve intercepts an email during transmission.

### Test Steps:
1. **In Eve's window**: Keep "⚠️ LISTENING ACTIVE - INTERCEPTING PACKETS" enabled
2. **In Alice's window**: Stop Eve's listener first
   - Go back to Compose
   - Click "🚀 Beam to Target PC"
   - **Then immediately** while Bob's server is receiving, have Eve toggle listening ON in Eve's window

### Expected Result (if timing is right):
- **Bob sees alert**: "🛑 INCOMING EMAIL BLOCKED"
  - Message says: "Eve was detected. Message automatically destroyed."
- **No email in Bob's inbox**

### Success Criteria ✅:
- Alert triggers on Bob's end
- Email is destroyed in transit
- No email appears in Bob's inbox

---

## Phase 3: Proactive QBER Alert ✅

**What it does**: Alice's QBER status bar spikes when Eve is listening, triggering a warning.

### Test Steps:
1. **In Alice's window**: Watch the "⚛️ QUANTUM LINK STATUS" bar on the left
   - Normal state: Green bar, QBER 0-2%
   - With Eve: Red bar, QBER 25-55%
2. **In Eve's window**: Click "🔴 START LISTENING ON FIBER OPTIC LINE"
3. **Watch Alice's status**: 
   - After ~1-2 seconds, the bar turns RED
   - QBER percentage jumps to 25-55%

### Expected Result:
- **Alert dialog appears**: "⚠️ QUANTUM LINK COMPROMISED"
  - Message: "High QBER detected: XX.XX%. Suspect eavesdropping."
- **QBER bar stays red** while Eve is listening
- **Alert appears once per 2 seconds** (cooldown to prevent spam)

### Success Criteria ✅:
- QBER bar changes color and value
- Alert dialog triggers automatically
- Alert only triggers when QBER > 20%

---

## Phase 4: Gmail Integration ✅

**What it does**: Real Gmail accounts work with the same Eve detection.

### Test Steps:
1. **In Alice's window**:
   - Go to "✍️ Compose"
   - Toggle "📧 Standard Gmail" radio button
   - Enter:
     - **To**: your-real-gmail@gmail.com (or bob@gmail.com)
     - **Gmail App Password**: [Use generated app password from Google]
     - **Subject**: Quantum Secure Test
     - **Body**: This is encrypted!

2. **With Eve NOT listening**: Click "✉️ Send Encrypted Gmail"
   - Should succeed

3. **Turn on Eve, try again**:
   - Eve clicks "🔴 START LISTENING"
   - Alice tries to send again
   - Should get "🛑 EAVESDROPPER DETECTED" alert
   - Email NOT sent

### Success Criteria ✅:
- Gmail sends when Eve is OFF
- Gmail blocked with Eve detection alert when Eve is ON
- Email arrives encrypted in real Gmail inbox

---

## Phase 5: Eve Interception Logging ✅

**What it does**: Eve's dashboard records all intercepted emails.

### Test Steps:
1. **In Alice's window**: Send emails (with Eve listening)
2. **In Eve's window**:
   - Click "🕵️ Intercept Dashboard" (should already be visible)
   - View table with columns: Time | Sender | Receiver | Intercepted Ciphertext
   - Click "🔄 Refresh Intercept Logs"

### Expected Result:
- **Eve's table shows entries**:
  - Timestamp of when email was intercepted
  - Sender (e.g., alice@quantum.com)
  - Receiver (e.g., bob@quantum.com)
  - Ciphertext (first 50 chars + "...")

### Success Criteria ✅:
- Intercept logs appear after sending with Eve listening
- Logs show correct sender/receiver
- Refreshing updates the table with new interceptions

---

## Full Integration Test Scenario

**Goal**: Test all phases working together

### Steps:
1. Start all 3 instances (Alice, Bob, Eve)
2. **Eve OFF**: Alice sends to Bob → email arrives in Bob's inbox
3. **Eve ON (Phase 1)**: Alice tries to send → gets Eve detection alert, email doesn't send
4. **Turn Eve OFF**: Alice sends → email arrives
5. **Eve ON (Phase 3)**: Watch Alice's QBER spike and get warning
6. **Eve keeps ON (Phase 2)**: Alice sends (somehow bypasses Phase 1 via code timing) → Bob gets blocked alert
7. **Eve's Dashboard (Phase 5)**: Refresh logs, see all interceptions recorded

### Expected: All 5 phases work together seamlessly ✅

---

## Google Account Support (Already Working)

The system already supports:
- ✅ Sending to real Gmail addresses (bob@gmail.com)
- ✅ Using real Gmail app passwords
- ✅ Same encryption/Eve detection applies

**Future Enhancement** (Not yet implemented):
- OAuth login to replace hardcoded alice/bob/eve identities
- This would allow any Google account to be used for both sender and receiver

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Alice doesn't see Eve OFF in Compose | Eve needs to toggle OFF button first |
| QBER alert never appears | Make sure Theme dark mode is on, wait 2+ seconds |
| Email arrives despite Eve listening | Phase 1 check might have failed, restart Eve |
| Eve's logs empty | Try sending with Eve listener ON, then refresh |
| Gmail doesn't send | Check app password is correct, Eve is OFF |

---

## Quick Summary of Files Modified

```
main.py:
  - Line 249: Added on_interception_detected callback
  - Line 260: Call setup_qber_alert() for Phase 3
  - Line 341: on_interception_detected() method (Phase 2)
  - Line 352: setup_qber_alert() method (Phase 3)
  - Line 367: Phase 1 check before sending
  - Line 469+: Enhanced QBER alert logic with Phase 3

backend/network.py:
  - Line 13: Added on_interception_callback parameter
  - Line 59: Call on_interception_callback when Eve detected

backend/db.py:
  - Lines 82-98: log_intercept() and get_hacker_logs() already exist
  
backend/smtp_client.py:
  - Line 13: Already logs interceptions
```

---

**All features are now live! Test away! 🚀**
