# streamlit_app.py
import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:9000"

st.set_page_config(page_title="Mavi AVM Chatbot", page_icon="🤖")
st.title("🤖 Mavi AVM Chatbot")

# Session state ile chat geçmişi ve kullanıcı verisi
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None

uploaded_file = st.file_uploader("Giriş için yüz fotoğrafınızı yükleyin", type=["jpg", "jpeg", "png"])

if uploaded_file and st.button("Giriş Yap"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/recognize/",
            files={"file": uploaded_file}
        )
        if response.status_code == 200 and "error" not in response.json():
            st.session_state.user_data = response.json()
            st.success(f"Hoş geldiniz, {st.session_state.user_data['name']}!")
        else:
            st.error(response.json().get("error", "Yüz tanıma sırasında bir hata oluştu."))
    except requests.exceptions.ConnectionError:
        st.error("API sunucusuna bağlanılamıyor. Backend çalışıyor mu?")

# -------------------------
# Chat kutusu
# -------------------------
if st.session_state.user_data:
    message = st.text_input(
        "Sormak istediğiniz bir yer var mı?",
        key="input_chat",  # Hatanın nedeni bu key'in yanlış kullanımını engelliyoruz
        value=""  # Başlangıçta boş
    )

    if st.button("Gönder") and message:
        try:
            chat_response = requests.post(
                f"{BACKEND_URL}/chat/{st.session_state.user_data['user_id']}",
                json={"message": message}
            )
            if chat_response.status_code == 200:
                bot_reply = chat_response.json().get("response", "Yanıt yok.")
                # Chat geçmişine ekle
                st.session_state.chat_history.append({"user": message, "bot": bot_reply})
            else:
                st.error("Mesaj gönderme sırasında hata oluştu.")
        except requests.exceptions.ConnectionError:
            st.error("API sunucusuna bağlanılamıyor.")

    # Chat geçmişini göster
    for chat in st.session_state.chat_history:
        st.markdown(f"**Siz:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
        st.markdown("---")
