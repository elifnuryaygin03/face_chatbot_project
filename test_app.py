import streamlit as st
import time

st.set_page_config(
    page_title="AVM Asistanı - Test Modu",
    page_icon="🏢",
    layout="wide"
)

st.title("AVM Asistanı - Test Modu")
st.write("Bu uygulama, API sunucusuna bağlanmadan çalışan test modudur.")

# Kullanıcı tanımlama
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Yüz tanıma butonu
if st.button("👤 Yüz Tanıma Başlat", use_container_width=True, type="primary"):
    with st.spinner("Yüz tanınıyor..."):
        time.sleep(1)  # Simülasyon gecikme
        st.session_state.user_id = 999
        st.success("Kullanıcı tanındı! (Test Modu)")
        st.rerun()

# Chatbot arayüzü
if st.session_state.user_id is not None:
    # Mesaj geçmişini göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Kullanıcı mesajı
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Kullanıcı mesajını göster
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Bot yanıtını üret
        with st.chat_message("assistant"):
            with st.spinner("Yanıt üretiliyor..."):
                time.sleep(0.5)  # Simülasyon gecikme

                # Test yanıtları
                responses = {
                    "merhaba": "Merhaba! Size nasıl yardımcı olabilirim?",
                    "selam": "Merhaba! Size nasıl yardımcı olabilirim?",
                    "eczane": "En yakın eczane AVM'nin batı çıkışında 200 metre ileridedir.",
                    "hastane": "En yakın hastane AVM'nin kuzeyinde 1 km mesafededir.",
                    "sinema": "Sinema 2. katta bulunmaktadır. Şu anda gösterimde olan filmler: Transformers, Hızlı ve Öfkeli, Barbie, Oppenheimer.",
                    "film": "Şu anda gösterimde olan filmler: Transformers, Hızlı ve Öfkeli, Barbie, Oppenheimer.",
                    "yemek": "Yemek katı 2. katta bulunmaktadır. Restoranlar: Burger King, McDonald's, Pizza Pizza, Domino's, Popeyes.",
                    "restoran": "Yemek katında Burger King, McDonald's, Pizza Pizza, Domino's, Popeyes gibi restoranlar bulunmaktadır.",
                    "kat": "AVM 5 kattan oluşmaktadır: -1 (otopark), 0 (giriş kat), 1 (giyim), 2 (yemek ve sinema), 3 (çocuk oyun alanı).",
                    "saat": "AVM her gün 10:00-22:00 saatleri arasında hizmet vermektedir.",
                    "giyim": "Giyim mağazaları 1. katta bulunmaktadır. Zara, H&M, Mavi, LC Waikiki, DeFacto gibi mağazalar mevcuttur.",
                    "market": "Market giriş katta (0. kat) bulunmaktadır. Migros ve Carrefour hizmet vermektedir.",
                    "teknoloji": "Teknoloji mağazaları giriş katta bulunmaktadır. MediaMarkt, Teknosa ve Vatan Bilgisayar gibi mağazalar mevcuttur.",
                    "oyun": "Çocuk oyun alanı 3. katta bulunmaktadır.",
                    "tuvalet": "Tuvaletler her katta bulunmaktadır. Size en yakın tuvalet yön tabelalarını takip ederek ulaşabilirsiniz."
                }

                response_found = False
                for key, response in responses.items():
                    if key in prompt.lower():
                        st.write(response)
                        response_found = True
                        break

                if not response_found:
                    st.write("Bu konuda size yardımcı olabilirim. Lütfen AVM hakkında sorular sorunuz.")

                # Yanıtı kaydet
                bot_response = response if response_found else "Bu konuda size yardımcı olabilirim. Lütfen AVM hakkında sorular sorunuz."
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
else:
    st.info("👆 Sohbete başlamak için lütfen önce yüz tanıma yapın.")

st.sidebar.title("Test Modu")
st.sidebar.info(
    "Bu uygulama API sunucusuna bağlanmadan çalışmaktadır. Gerçek veritabanı yerine test verileri kullanılmaktadır.")

# Footer
st.markdown("---")
st.caption("Mavi Vadi AVM Test Asistanı © 2025")