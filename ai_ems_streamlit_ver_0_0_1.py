# app.py

import streamlit as st
import whisper
import os
import requests
import json
import tempfile
import email

# -----------------------------
# 🎨 Streamlit UI
# -----------------------------
st.set_page_config(page_title="Meeting & Email Summarizer", layout="centered")
st.title("📋 Meeting & Email Summarizer")
st.markdown("Upload a **recording (.mp3, .wav, .mp4)**, **text file (.txt)**, or **email (.eml)** to generate action items and summaries.")

# -----------------------------
# 📁 Upload File
# -----------------------------
uploaded_file = st.file_uploader("Upload a file", type=["mp3", "wav", "mp4", "txt", "eml"])

if uploaded_file:
    file_type = uploaded_file.name.lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    # -----------------------------
    # 🎧 Transcribe or Read
    # -----------------------------
    if file_type.endswith(('.mp3', '.wav', '.mp4')):
        st.info("Transcribing audio using Whisper...")
        model = whisper.load_model("base")  # or "tiny"
        result = model.transcribe(file_path)
        transcript = result["text"]

    elif file_type.endswith('.eml'):
        st.info("Reading email content...")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            msg = email.message_from_file(f)
            if msg.is_multipart():
                parts = [part.get_payload(decode=True).decode(errors='ignore') for part in msg.walk() if part.get_content_type() == 'text/plain']
                transcript = "\n".join(parts)
            else:
                transcript = msg.get_payload(decode=True).decode(errors='ignore')

    elif file_type.endswith('.txt'):
        st.info("Reading text file...")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            transcript = f.read()

    else:
        st.error("Unsupported file type.")
        st.stop()

    # -----------------------------
    # 💬 Display Transcript Preview
    # -----------------------------
    st.subheader("📄 Transcript Preview")
    st.text_area("Transcript", transcript[:1000], height=250)

    # -----------------------------
    # 🔑 Together API Setup (API key directly in code)
    # -----------------------------
    api_key = "895b590f32d6475e94c42ecd8c42ab90b0b83c507bea5ef59b9748a5787f38c5"  # <-- Your API key here
    together_url = "https://api.together.xyz/v1/chat/completions"

    prompt = f"""
    You are an executive assistant AI. The following is a transcript of a client meeting or email.

    Extract and format:
    1. Summary of key discussion points
    2. Action items with who is responsible
    3. Deadlines or important dates (if mentioned)
    4. Risks or open questions

    Meeting Transcript:
    {transcript}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 700
    }

    if st.button("🧠 Generate Summary"):
        with st.spinner("Calling Together.ai..."):
            response = requests.post(together_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                ai_output = response.json()['choices'][0]['message']['content']
                st.subheader("📝 Summary & Action Items")
                st.text(ai_output)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
