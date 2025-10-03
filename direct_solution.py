import streamlit as st
import time

# Sayfa başlığı ve yapılandırması
st.set_page_config(page_title="AVM Chatbot", page_icon="🏢", layout="centered")

# AVM bilgileri
AVM_DATA = {
    "isim": "Mavi Vadi AVM",
    "saat": "10:00-22:00",
    "kat_sayisi": 5,
    "katlar": {
        "-1": "Otopark",
        "0": "Giriş kat - Marketler ve Teknoloji Mağazaları",
        "1": "1. kat - Giyim Mağazaları",
        "2": "2. kat - Yemek Katı ve Sinema",
        "3": "3. kat - Çocuk Oyun Alanı ve Etkinlik Alanı"
    },
    "yerler": {
        "eczane": "AVM'nin batı çıkışında 200 metre ileride. AVM'den çıktıktan sonra sağa dönüp 200 metre düz gitmeniz gerekiyor.",
        "hastane": "AVM'nin kuzeyinde 1 km mesafede. AVM'den çıkıp ana caddeye çıkın ve sola dönün. 10-15 dakikalık yürüme mesafesinde.",
        "yemek": "Yemek katı 2. katta bulunuyor. Asansör veya yürüyen merdivenlerle ulaşabilirsiniz.",
        "sinema": "Sinema 2. katta bulunuyor. Biletler gişeden veya mobil uygulamamızdan alınabilir.",
        "tuvalet": "Tuvaletler her katta bulunuyor. Yön tabelalarını takip ederek en yakın tuvalete ulaşabilirsiniz.",
        "otopark": "Otopark -1. katta bulunuyor. Giriş ve çıkışlar AVM'nin kuzey ve güney taraflarında.",
        "oyun": "Çocuk oyun alanı 3. katta bulunuyor. Asansör veya yürüyen merdivenle ulaşabilirsiniz.",
        "atm": "ATM'ler giriş katta ve 2. kattaki banka şubesinin yanında bulunuyor."
    },
    "mağazalar": {
        "giyim": ["DeFacto", "LC Waikiki", "Koton", "Mavi", "Zara", "H&M"],
        "teknoloji": ["MediaMarkt", "Teknosa", "Vatan Bilgisayar"],
        "market": ["Migros", "Carrefour"],
        "restoran": ["Burger King", "McDonald's", "Pizza Pizza", "Domino's Pizza", "Popeyes", "Köfteci Yusuf",
                     "Baydöner"]
    },
    "filmler": [
        "Transformers: Yeni Nesil",
        "Hızlı ve Öfkeli 10",
        "Barbie",
        "Oppenheimer",
        "Mega Fırlatıcı"
    ],
    "restoran_türleri": {
        "fast_food": ["Burger King", "McDonald's", "Popeyes"],
        "pizza": ["Pizza Pizza", "Domino's Pizza"],
        "türk_mutfağı": ["Köfteci Yusuf", "Baydöner"]
    }
}

# Kullanıcı bilgilerini saklamak için sözlük
user_data = {}


def generate_response(message, user_name=None):
    """
    Kullanıcının mesajına yanıt üretir.
    """
    # Mesajı küçük harfe çevir
    message_lower = message.lower()

    print(f"[DEBUG] İşlenen mesaj: {message_lower}")

    # İsim tanıma
    if ("adım" in message_lower or "ismim" in message_lower):
        words = message_lower.split()
        for i, word in enumerate(words):
            if word in ["adım", "ismim"]:
                if i + 1 < len(words):
                    return f"Memnun oldum {words[i + 1].capitalize()}! Size nasıl yardımcı olabilirim?"

    # Selamlaşma
    if any(word in message_lower for word in ["merhaba", "selam", "merhabalar", "hi", "hey"]):
        if user_name:
            return f"Merhaba {user_name}! Size nasıl yardımcı olabilirim?"
        else:
            return "Merhaba! Size nasıl yardımcı olabilirim?"

    # Teşekkür
    if any(word in message_lower for word in ["teşekkür", "sağol", "teşekkürler"]):
        return "Rica ederim! Başka bir konuda yardımcı olabilir miyim?"

    # ECZANE SORGUSU
    if any(word in message_lower for word in ["eczane", "ilaç", "pharmacy", "eczaneye", "ecza"]):
        return f"En yakın eczane {AVM_DATA['yerler']['eczane']}"

    # HASTANE SORGUSU
    if any(word in message_lower for word in ["hastane", "doktor", "sağlık", "acil", "ambulans"]):
        return f"En yakın hastane {AVM_DATA['yerler']['hastane']}"

    # FİLM SORGUSU
    if any(word in message_lower for word in ["film", "filmler", "vizyon", "sinema filmleri"]):
        return "Şu anda gösterimde olan filmler: " + ", ".join(AVM_DATA["filmler"])

    # "Hangi" ve "var" soruları için özel kontrol
    if "hangi" in message_lower and "var" in message_lower:
        if "film" in message_lower:
            return "Şu anda gösterimde olan filmler: " + ", ".join(AVM_DATA["filmler"])
        if any(word in message_lower for word in ["yemek", "restoran", "kafe", "cafe", "yiyecek"]):
            return f"Yemek katımızda şu restoranlar bulunmaktadır: {', '.join(AVM_DATA['mağazalar']['restoran'])}"
        if "mağaza" in message_lower or "giyim" in message_lower:
            return f"Giyim mağazalarımız: {', '.join(AVM_DATA['mağazalar']['giyim'])}"
        if "teknoloji" in message_lower or "elektronik" in message_lower:
            return f"Teknoloji mağazalarımız: {', '.join(AVM_DATA['mağazalar']['teknoloji'])}"

    # NE soruları için özel kontrol
    if "ne" in message_lower:
        if any(word in message_lower for word in ["yemek", "restoran", "kafe", "cafe", "yiyecek"]):
            if "var" in message_lower or "tür" in message_lower:
                return f"Yemek katımızda şu restoranlar bulunmaktadır: {', '.join(AVM_DATA['mağazalar']['restoran'])}"

    # SİNEMA SORGUSU
    if "sinema" in message_lower:
        # Eğer "nerede" gibi konum sorusu ise
        if any(word in message_lower for word in ["nerede", "nereye", "nasıl", "gidebilirim", "kat", "katta"]):
            return AVM_DATA["yerler"]["sinema"]
        # Genel sinema sorusu
        return f"Sinema 2. katta bulunuyor. Şu anda gösterimde olan filmler: {', '.join(AVM_DATA['filmler'])}"

    # FAST FOOD SORGUSU
    if "fast" in message_lower or "food" in message_lower or "fast food" in message_lower:
        fast_food_list = AVM_DATA["restoran_türleri"]["fast_food"]
        if any(word in message_lower for word in ["nerede", "kat", "nasıl", "gidebilirim"]):
            return f"Fast food restoranları 2. kattaki yemek alanında bulunmaktadır."
        return f"Fast food restoranlarımız: {', '.join(fast_food_list)}. Bunlar 2. kattaki yemek alanında bulunmaktadır."

    # TÜRK MUTFAĞI SORGUSU
    if "türk" in message_lower or "kebap" in message_lower or "köfte" in message_lower or "döner" in message_lower:
        return f"Türk mutfağı restoranlarımız: {', '.join(AVM_DATA['restoran_türleri']['türk_mutfağı'])}. Bunlar 2. kattaki yemek alanında bulunmaktadır."

    # PIZZA SORGUSU
    if "pizza" in message_lower:
        return f"Pizza restoranlarımız: {', '.join(AVM_DATA['restoran_türleri']['pizza'])}. Bunlar 2. kattaki yemek alanında bulunmaktadır."

    # YER BİLGİLERİ
    for yer, bilgi in AVM_DATA["yerler"].items():
        if yer in message_lower or any(alt_word in message_lower for alt_word in [
            f"{yer}ye", f"{yer}ya", f"{yer}e", f"{yer}a",
            f"{yer} nerede", f"{yer} nerede?", f"{yer} nerdedir"
        ]):
            return bilgi

    # KAT BİLGİLERİ
    if "kat" in message_lower:
        # Belirli bir kat soruluyorsa
        for kat in AVM_DATA["katlar"]:
            if kat in message_lower or f"{kat}." in message_lower:
                return f"{kat}. kat: {AVM_DATA['katlar'][kat]}"

        # Eğer yemek veya sinema ile ilgili kat soruluyorsa
        if "yemek" in message_lower:
            return f"Yemek katı 2. katta bulunmaktadır. {AVM_DATA['yerler']['yemek']}"

        if "sinema" in message_lower:
            return f"Sinema 2. katta bulunmaktadır. {AVM_DATA['yerler']['sinema']}"

        # Genel kat bilgisi - daha düzenli format
        kat_bilgileri = []
        for k, v in AVM_DATA["katlar"].items():
            kat_bilgileri.append(f"{k}. kat: {v}")
        return "\n".join(kat_bilgileri)

    # ÇALIŞMA SAATLERİ
    if any(word in message_lower for word in ["saat", "açık", "kapanış", "kaçta", "ne zaman"]):
        return f"AVM'miz her gün {AVM_DATA['saat']} saatleri arasında hizmet vermektedir."

    # MAĞAZALAR HAKKINDA
    for kategori, magazalar in AVM_DATA["mağazalar"].items():
        if kategori in message_lower:
            return f"{kategori.capitalize()} mağazalarımız: {', '.join(magazalar)}"

    # YEMEK SORGUSU - GELİŞTİRİLMİŞ
    if any(word in message_lower for word in ["restoran", "yemek", "kafe", "cafe", "yiyecek", "acıktım", "karnım aç"]):
        # Konum soruluyorsa
        if any(word in message_lower for word in ["nerede", "nereye", "nasıl", "gidebilirim", "kat", "katta"]):
            return AVM_DATA["yerler"]["yemek"]
        # Yemek türleri soruluyorsa
        elif any(word in message_lower for word in
                 ["ne tür", "neler var", "hangi", "çeşit", "ne yemek", "var mı", "listesi", "menü"]):
            return f"Yemek katımızda şu restoranlar bulunmaktadır: {', '.join(AVM_DATA['mağazalar']['restoran'])}"
        # Genel yemek sorusu
        return f"Yemek katı 2. katta bulunuyor. Restoranlarımız arasında {', '.join(AVM_DATA['mağazalar']['restoran'])} bulunmaktadır."

    # GİYİM MAĞAZALARI SORGUSU - GELİŞTİRİLMİŞ
    if "giyim" in message_lower or "kıyafet" in message_lower or "elbise" in message_lower:
        if "nerede" in message_lower or "hangi kat" in message_lower:
            return "Giyim mağazaları 1. katta bulunmaktadır."
        else:
            return f"Giyim mağazalarımız: {', '.join(AVM_DATA['mağazalar']['giyim'])}. Bunlar 1. katta bulunmaktadır."

    # Genel AVM bilgisi
    if "avm" in message_lower:
        return f"{AVM_DATA['isim']} {AVM_DATA['kat_sayisi']} kattan oluşmaktadır. Çalışma saatlerimiz {AVM_DATA['saat']} arasındadır. Size nasıl yardımcı olabilirim?"

    # Varsayılan yanıt - daha spesifik yönlendirme
    return "Mavi Vadi AVM asistanı olarak size yardımcı olmak için buradayım. Mağazalar, restoranlar, sinema, eczane veya diğer hizmetler hakkında bilgi verebilirim. Örneğin 'Hangi restoranlar var?', 'Sinemada hangi filmler oynuyor?' veya 'Eczaneye nasıl giderim?' gibi sorular sorabilirsiniz."


# Başlık ve açıklama
st.title('Yüz Tanıma Chatbot Uygulaması')
st.write('Bu uygulama yüz tanıma ve chatbot özelliklerini bir araya getirir.')

# Session state değişkenlerini başlat
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'user_name' not in st.session_state:
    st.session_state.user_name = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Yüz tanıma kısmı
if st.button('Yüz Tanıma Başlat'):
    with st.spinner("Yüz tanıma işlemi başlatılıyor..."):
        # Basit bir gecikme ekleyerek tanıma simülasyonu
        time.sleep(1)
        st.session_state.user_id = 1
        st.success(f"Kullanıcı tanındı! User ID: {st.session_state.user_id}")
        # Güncellenmiş rerun metodu
        st.rerun()

# Kullanıcı tanındıysa sohbet arayüzünü göster
if st.session_state.user_id is not None:
    # Kullanıcı bilgilerini göster
    st.subheader(f"Kullanıcı #{st.session_state.user_id}")

    # Sekme arayüzü
    tab1, tab2 = st.tabs(["Sohbet", "Geçmiş"])

    with tab1:
        # Mevcut mesajları göster
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

        # Yeni mesaj girişi
        if prompt := st.chat_input("Mesajınızı girin"):
            # Kullanıcı adını kontrol etmek için
            if st.session_state.user_name is None:
                words = prompt.lower().split()
                if "adım" in words or "ismim" in words:
                    for i, word in enumerate(words):
                        if word in ["adım", "ismim"]:
                            if i + 1 < len(words):
                                st.session_state.user_name = words[i + 1].capitalize()

            # Kullanıcı mesajını göster
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # Yanıt oluştur
            with st.spinner("Yanıt üretiliyor..."):
                bot_response = generate_response(prompt, st.session_state.user_name)

                # Bot yanıtını göster
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                st.chat_message("assistant").write(bot_response)

    with tab2:
        st.subheader("Sohbet Geçmişi")
        if st.session_state.messages:
            for i, message in enumerate(st.session_state.messages):
                role = "Kullanıcı" if message["role"] == "user" else "Bot"
                st.text(f"{role}: {message['content']}")
                if i < len(st.session_state.messages) - 1:
                    st.divider()
        else:
            st.info("Henüz sohbet geçmişi bulunmuyor.")
else:
    st.info("Sohbete başlamak için önce yüz tanıma yapmalısınız.")

# Footer
st.markdown("---")
st.caption("Mavi Vadi AVM Asistanı - 2025")