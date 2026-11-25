# 🏪 VoiceLedger AI
### Your Voice-Powered Business Manager for Indian Shopkeepers
> Built for **Scaler × Wispr Flow Hackathon 2026** | Track: Small Business

---

## 🎯 Problem
Over **60 million kirana store owners** in India still manage accounts manually with paper ledgers.
Existing digital tools require reading/typing in English — a barrier for shopkeepers who are more
comfortable speaking their regional language.

## ✅ Solution
**VoiceLedger AI** lets shopkeepers manage their entire business just by speaking in
**Hindi, Gujarati, or English** — no typing, no English required.

### Key Features
| Feature | Description |
|---|---|
| 🎙️ Voice Transactions | Say *"Becha 5 kg aata 100 rupees"* → auto-saved |
| 🧠 AI Understanding | Gemini LLM extracts item, quantity, price from natural speech |
| 📦 Auto Inventory | Stock updates automatically on every sale/purchase |
| ⚠️ Low Stock Alerts | Visual + voice alerts when items run low |
| 📊 Daily P&L | Spoken profit & loss summary on demand |
| 🔊 Voice Reports | Complete daily business report read aloud in Hindi |
| ⌨️ Manual Fallback | Type-in option for when voice isn't convenient |

---

## 🛠️ Tech Stack & Wispr Flow Integration

| Tool | Purpose | How It's Used |
|---|---|---|
| **Wispr Flow (Desktop App)** | AI-powered voice dictation for users & rapid prototyping | Used with promo code `FLOW4SCALER` to provide continuous dictation into VoiceLedger's interface and developer workflow |
| **Google Speech Recognition / Web Audio** | In-app audio capture and STT pipeline | Captures in-browser audio streams directly from microphone across Hindi, Gujarati, and English |
| **Google Gemini 3.8 Flash** | Transaction Intelligence & RAG Brain | Parses intent, normalizes currency, extracts SKU/quantity, and answers shopkeeper business queries |
| **SQLite** | Local Database | Stores ledger transactions and inventory state |
| **gTTS & Windows Media** | Spoken Audio Feedback | Confirms transactions and reads aloud P&L summaries in Hindi |
| **Streamlit** | Interactive Web Dashboard | Provides clean, accessible UI for Kirana store operators |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/VoiceLedger-AI.git
cd VoiceLedger-AI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_key_here
WISPR_API_KEY=your_wispr_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🎙️ Built with Wispr Flow
* **Wispr Flow Pro Integration**: Activated with code `FLOW4SCALER`.
* **Universal Dictation**: Any Kirana operator using the Wispr Flow desktop app can place their cursor on VoiceLedger AI or their POS screens to dictate entries instantly in natural regional vernacular.
* **Autonomous Speech Pipeline**: Built-in web audio + STT and Gemini 3.8 Flash intelligence handles autonomous parsing, inventory deduction, and vocal read-back.

| Command (Hindi) | What Happens |
|---|---|
| *"Becha 5 kg aata 100 rupees mein"* | Records sale: flour, 5kg, ₹100 |
| *"Kharida 2 litre tel 180 rupaye"* | Records expense: oil, 2L, ₹180 |
| *"Aaj kitna profit hua?"* | AI reads today's net profit |
| *"Konsa item kam hai?"* | Shows low stock items |
| *"Daily report sunao"* | Full business summary spoken aloud |

---

## 🏗️ Architecture

```
Shopkeeper speaks
      ↓
Wispr Flow API (multilingual STT, context-aware)
      ↓
Google Gemini LLM (parse intent + extract data)
      ↓
SQLite Database (save transaction, update inventory)
      ↓
gTTS (speak confirmation back)
      ↓
Streamlit Dashboard (visual summary)
```

---

## 🌍 Target Users
- Kirana stores
- Small retailers
- Street vendors
- Local businesses across India

## 📈 Expected Impact
Make digital business management accessible to **60M+ small businesses** across India,
in their own language, without needing to learn accounting software.

---

## 👩‍💻 Team
- Vaishali Mali
