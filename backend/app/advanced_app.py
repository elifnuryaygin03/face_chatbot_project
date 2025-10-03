import streamlit as st
from chatbot import generate_response
import json
from datetime import datetime
import os

# ---- CANLI RENKLERLE ARKA PLAN VE BAŞLIKLAR ----
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #cffbfc 0%, #f6d365 100%);
        min-height: 100vh;
    }
    .block-container {
        padding-top: 2rem;
    }
    .special-title {
        background-color: #f67280;
        color: white;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        font-size: 2.1em;
        font-weight: bold;
        text-align: center;
        letter-spacing: 2px;
        box-shadow: 0 4px 24px 0 rgba(0,0,0,0.09);
    }
    .chat-header {
        background: #36d1c4;
        color: white;
        padding: 12px;
        border-radius: 12px;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 18px;
        margin-top: 32px;
        text-align: center;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True
)

# ---- SAYFA BAŞLIĞI ----
st.markdown('<div class="special-title">💡 Mavi Vadi AVM Akıllı Sohbet Asistanı</div>', unsafe_allow_html=True)

# ---- AVM DATA YÜKLEME ----
try:
    dosya_yolu = os.path.join(os.path.dirname(__file__), "avm_data.json")
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        AVM_DATA = json.load(f)
    st.success("AVM verisi başarıyla yüklendi.")
except Exception as e:
    st.error(f"AVM verileri yüklenemedi: {e}")

st.sidebar.success("Hoş geldiniz! Buradan menüyü ve diğer AVM modüllerini kullanabilirsiniz.")

# ---- FOTOĞRAF YÜKLEME ----
uploaded_file = st.file_uploader("💎 AVM'ye giriş için yüz fotoğrafınızı yükleyin", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.info("✨ Yüz fotoğrafınız başarıyla yüklendi!")
    if st.button("🟩 Sohbete Başla"):
        st.session_state["sohbet"] = True

# ---- SOHBET KUTUSU ----
if st.session_state.get("sohbet", False):
    st.markdown('<div class="chat-header">💬 Chatbot ile Sohbet Başlatın</div>', unsafe_allow_html=True)
    user_id = 1  # İsterseniz dinamikleştirilebilir
    message = st.text_input("Sorunuzu yazınız:", key="mesaj")
    if st.button("✉️ Mesajı Gönder"):
        yanit = generate_response(user_id, message)
        # Kullanıcı mesajı ve bot cevabını kutuda göster:
        st.markdown(
            f'<div style="background-color:#ffb347; color:black; padding:13px; border-radius:9px; margin-bottom:10px; font-weight:600;">'
            f"Siz: {message}"
            '</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="background-color:#36d1c4; color:white; padding:13px; border-radius:9px; margin-bottom:18px; font-weight:600;">'
            f"Bot : {yanit}"
            '</div>', unsafe_allow_html=True)
        # Chat geçmişi için session_state'e ekleyebilirsin

# ---- EXTRA: LOGO veya RENKLİ ALAN EKLEMEK ister misin? ----
# st.image("logo.png", width=160) gibi bir satır ekleyebilirsin.