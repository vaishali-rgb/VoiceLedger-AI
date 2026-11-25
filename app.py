import streamlit as st
import os
from streamlit_mic_recorder import mic_recorder
from database import init_db, save_transaction, get_todays_summary, get_low_stock_items, get_all_transactions, get_inventory
from voice import save_audio_bytes, process_audio_file
from ai_brain import parse_transaction, answer_business_query, generate_daily_report
from tts import speak

# ── Bootstrap ────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
os.makedirs("audio", exist_ok=True)
init_db()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceLedger AI",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size:2.5rem; font-weight:700; color:#1a73e8; }
    .sub-title  { font-size:1rem; color:#666; margin-top:-10px; }
    .metric-box { background:#f0f7ff; border-radius:12px; padding:16px; text-align:center; }
    .stButton>button { border-radius:10px; font-size:1rem; height:3rem; }
    .success-box { background:#e6f4ea; border-left:4px solid #34a853;
                   padding:12px; border-radius:8px; margin:8px 0; }
    .alert-box  { background:#fce8e6; border-left:4px solid #ea4335;
                  padding:12px; border-radius:8px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shop.png", width=80)
    st.markdown("## 🏪 VoiceLedger AI")
    st.caption("Voice-powered business manager for Indian shopkeepers")
    st.divider()

    lang_map = {
        "🇮🇳 Hindi":   "hi",
        "🌐 English":  "en",
        "Gujarati":    "gu",
    }
    selected_lang_label = st.selectbox("🗣️ Language / भाषा:", list(lang_map.keys()))
    language_code = lang_map[selected_lang_label]

    st.divider()
    st.markdown("### ℹ️ Voice Commands")
    st.markdown("""
**Sales:**
> *"Becha 5 kg aata 100 rupees mein"*

**Expenses:**
> *"Kharida 2 litre tel 180 rupaye"*

**Ask anything:**
> *"Aaj kitna profit hua?"*
> *"Konsa item kam hai?"*
    """)

    st.divider()
    st.caption("🛠️ Powered by Wispr Flow + Google Gemini")

# ── Main header ───────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🏪 VoiceLedger AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Your voice-powered business manager · Hindi · Gujarati · English</p>', unsafe_allow_html=True)
st.divider()

# ── Low stock alerts (shown at top if any) ────────────────────────────────────
low_stock = get_low_stock_items()
if low_stock:
    with st.expander("⚠️ Low Stock Alerts", expanded=True):
        for item, item_hindi, qty, unit, threshold in low_stock:
            name = item_hindi or item
            st.markdown(
                f'<div class="alert-box">⚠️ <b>{name}</b> — only <b>{qty} {unit or ""}</b> left '
                f'(threshold: {threshold} {unit or ""})</div>',
                unsafe_allow_html=True
            )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🎙️ Record Transaction", "📊 Summary & Report", "📦 Inventory", "📋 All Transactions"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Record voice transaction
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🎙️ Record a Transaction by Voice")
    st.info("Press the button, speak your transaction in Hindi/Gujarati/English, and VoiceLedger will save it automatically.")

    col_rec, col_ask = st.columns(2)

    # ── Record sale/expense ──────────────────────────────────────────────────
    with col_rec:
        st.markdown("#### 💰 Record Sale or Expense")
        st.caption("Click to record your voice from browser:")
        audio_record = mic_recorder(
            start_prompt="🎙️ Start Speaking",
            stop_prompt="⏹️ Stop & Process",
            key="rec_transaction"
        )

        if audio_record and "bytes" in audio_record:
            audio_path = save_audio_bytes(audio_record["bytes"])
            with st.spinner("🎧 Transcribing audio with Wispr/STT..."):
                spoken_text = process_audio_file(audio_path, language_code=language_code)

            if spoken_text:
                st.markdown(f"**📝 You said:** `{spoken_text}`")

                with st.spinner("🧠 Gemini is understanding your command..."):
                    parsed = parse_transaction(spoken_text)

                st.json(parsed)

                t_type = parsed.get("type")
                price  = parsed.get("price")

                if t_type in ("sale", "expense") and price:
                    item       = parsed.get("item") or "unknown"
                    item_hindi = parsed.get("item_hindi") or item
                    quantity   = parsed.get("quantity")
                    unit       = parsed.get("unit")

                    save_transaction(t_type, item, item_hindi, quantity, unit, float(price))

                    emoji = "💰" if t_type == "sale" else "💸"
                    confirm_en = f"{emoji} {t_type.capitalize()} recorded! {item_hindi} — ₹{price:.0f}"

                    if language_code == "hi":
                        confirm_speak = f"{item_hindi} ka {t_type} record ho gaya. Rakam: {price:.0f} rupaye."
                    elif language_code == "gu":
                        confirm_speak = f"{item_hindi} no {t_type} save thayo. Rakam: {price:.0f} rupiya."
                    else:
                        confirm_speak = confirm_en

                    st.markdown(f'<div class="success-box">{confirm_en}</div>', unsafe_allow_html=True)
                    speak(confirm_speak, language=language_code)

                elif t_type == "query":
                    st.info("💬 That sounded like a question — please use the 'Ask a Question' section.")
                else:
                    st.warning("⚠️ Could not understand the transaction. Please try again.")
            else:
                st.error("❌ Could not recognize speech. Please speak clearly into your mic.")

    # ── Ask a question ───────────────────────────────────────────────────────
    with col_ask:
        st.markdown("#### 💬 Ask a Question by Voice")
        st.caption("Ask questions about profit, stock, sales:")
        audio_query = mic_recorder(
            start_prompt="🎙️ Ask by Voice",
            stop_prompt="⏹️ Stop & Answer",
            key="rec_query"
        )

        if audio_query and "bytes" in audio_query:
            audio_path = save_audio_bytes(audio_query["bytes"])
            with st.spinner("🎧 Transcribing your question..."):
                question_text = process_audio_file(audio_path, language_code=language_code)

            if question_text:
                st.markdown(f"**❓ Question:** `{question_text}`")
                db_data = get_todays_summary()

                with st.spinner("🧠 Gemini is thinking..."):
                    answer = answer_business_query(question_text, db_data)

                st.markdown(f'<div class="success-box">🤖 <b>VoiceLedger:</b><br>{answer}</div>',
                            unsafe_allow_html=True)
                speak(answer, language=language_code)
            else:
                st.error("❌ Could not recognize speech. Please try again.")

    # ── Manual entry fallback ────────────────────────────────────────────────
    st.divider()
    with st.expander("⌨️ Prefer to type? Enter manually"):
        with st.form("manual_form"):
            m_type  = st.selectbox("Type", ["sale", "expense"])
            m_item  = st.text_input("Item (Hindi name)", placeholder="e.g. aata")
            m_item_en = st.text_input("Item (English)", placeholder="e.g. flour")
            m_qty   = st.number_input("Quantity", min_value=0.0, step=0.5)
            m_unit  = st.selectbox("Unit", ["kg", "litre", "piece", "packet", "dozen", "other"])
            m_price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
            submitted = st.form_submit_button("💾 Save Transaction")

            if submitted and m_price > 0 and m_item:
                save_transaction(m_type, m_item_en or m_item, m_item,
                                 m_qty if m_qty > 0 else None, m_unit, m_price)
                st.success(f"✅ Saved: {m_type} of {m_item} — ₹{m_price:.0f}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Summary & Report
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Today's Business Summary")

    summary_text = get_todays_summary()

    # Parse numbers for metric cards
    lines = summary_text.splitlines()
    sales_val = exp_val = profit_val = 0.0
    for line in lines:
        if "Total Sales" in line:
            try: sales_val = float(line.split("₹")[1])
            except: pass
        elif "Total Expenses" in line:
            try: exp_val = float(line.split("₹")[1])
            except: pass
        elif "Net Profit" in line:
            try: profit_val = float(line.split("₹")[1])
            except: pass

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💰 Total Sales",    f"₹{sales_val:,.0f}")
    with c2:
        st.metric("💸 Total Expenses", f"₹{exp_val:,.0f}")
    with c3:
        color = "normal" if profit_val >= 0 else "inverse"
        st.metric("📈 Net Profit",     f"₹{profit_val:,.0f}", delta_color=color)

    st.text(summary_text)

    st.divider()
    if st.button("🔊 Read Out Daily Report", use_container_width=True):
        with st.spinner("📢 Generating spoken report..."):
            report = generate_daily_report(summary_text)
        st.markdown(f'<div class="success-box">{report}</div>', unsafe_allow_html=True)
        speak(report, language=language_code)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Inventory
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📦 Inventory Status")

    inventory = get_inventory()
    if inventory:
        import pandas as pd
        df = pd.DataFrame(inventory, columns=["Item (Hindi)", "Item (English)", "Stock", "Unit", "Low Stock Alert"])
        df["Status"] = df.apply(
            lambda r: "⚠️ Low" if r["Stock"] <= r["Low Stock Alert"] else "✅ OK", axis=1
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No inventory data yet. Record some transactions to auto-build your inventory.")

    st.divider()
    with st.expander("⚙️ Set Low Stock Threshold"):
        import sqlite3
        from database import DB_PATH
        inv = get_inventory()
        if inv:
            item_names = [f"{r[0]} ({r[1]})" for r in inv]
            sel = st.selectbox("Select item:", item_names)
            new_threshold = st.number_input("New threshold:", min_value=0.0, step=1.0)
            if st.button("Update Threshold"):
                idx = item_names.index(sel)
                item_en = inv[idx][1]
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE inventory SET low_stock_threshold=? WHERE item=?",
                             (new_threshold, item_en))
                conn.commit(); conn.close()
                st.success(f"✅ Threshold for {sel} updated to {new_threshold}")
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — All Transactions
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📋 Transaction History")

    txns = get_all_transactions(limit=100)
    if txns:
        import pandas as pd
        df = pd.DataFrame(txns, columns=["Date", "Time", "Type", "Item", "Qty", "Unit", "Price (₹)"])
        df["Type"] = df["Type"].apply(lambda x: "💰 Sale" if x == "sale" else "💸 Expense")
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No transactions recorded yet. Go to the Record tab and speak your first transaction!")
