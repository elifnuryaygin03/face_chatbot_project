# backend/app/chatbot.py
# Sadece kural tabanlı, dış servislere bağımlılığı olmayan chatbot

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
    ]
}

# Kullanıcı bilgilerini saklamak için sözlük
user_data = {}


def generate_response(user_id, message, history=None):

    print(f"[INFO] Mesaj alındı: '{message}'")

    # Kullanıcı bilgilerini başlat veya güncelle
    if user_id not in user_data:
        user_data[user_id] = {
            "name": None,
            "last_queries": []
        }

    # Son mesajı kaydet
    user_data[user_id]["last_queries"].append(message)
    if len(user_data[user_id]["last_queries"]) > 5:  # En fazla son 5 mesajı tut
        user_data[user_id]["last_queries"].pop(0)

    # Mesajı küçük harfe çevir
    message_lower = message.lower()

    print(f"[DEBUG] Mesaj analiz ediliyor: '{message_lower}'")

    # İsim tanıma
    if ("adım" in message_lower or "ismim" in message_lower):
        words = message_lower.split()
        for i, word in enumerate(words):
            if word in ["adım", "ismim"]:
                if i + 1 < len(words):
                    user_data[user_id]["name"] = words[i + 1].capitalize()
                    return f"Memnun oldum {user_data[user_id]['name']}! Size nasıl yardımcı olabilirim?"

    # Selamlaşma
    if any(word in message_lower for word in ["merhaba", "selam", "merhabalar", "hi", "hey"]):
        if user_data[user_id].get("name"):
            return f"Merhaba {user_data[user_id]['name']}! Size nasıl yardımcı olabilirim?"
        else:
            return "Merhaba! Size nasıl yardımcı olabilirim?"

    # Teşekkür
    if any(word in message_lower for word in ["teşekkür", "sağol", "teşekkürler"]):
        return "Rica ederim! Başka bir konuda yardımcı olabilir miyim?"

    # ECZANE SORGUSU - Bu kısmı özellikle güçlendirelim
    if "eczane" in message_lower:
        print("[DEBUG] Eczane kelimesi bulundu!")
        return f"En yakın eczane {AVM_DATA['yerler']['eczane']}"

    # İlaçla ilgili sorular da eczaneye yönlendirilsin
    if any(word in message_lower for word in ["ilaç", "pharmacy", "reçete", "ecza"]):
        return f"İlaç ihtiyaçlarınız için, en yakın eczane {AVM_DATA['yerler']['eczane']}"

    # HASTANE SORGUSU
    if any(word in message_lower for word in ["hastane", "doktor", "sağlık", "acil", "ambulans"]):
        return f"En yakın hastane {AVM_DATA['yerler']['hastane']}"

    # FİLM SORGUSU - Bu kısmı da güçlendirelim
    if "film" in message_lower:
        print("[DEBUG] Film kelimesi bulundu!")
        return "Şu anda gösterimde olan filmler: " + ", ".join(AVM_DATA["filmler"])

    # "Hangi filmler var" sorusunu ele alalım
    if "hangi" in message_lower and "var" in message_lower:
        return "Şu anda gösterimde olan filmler: " + ", ".join(AVM_DATA["filmler"])

    # YER BİLGİLERİ
    for yer, bilgi in AVM_DATA["yerler"].items():
        if yer in message_lower or any(alt_word in message_lower for alt_word in [
            f"{yer}ye", f"{yer}ya", f"{yer}e", f"{yer}a",
            f"{yer} nerede", f"{yer} nerede?", f"{yer} nerdedir"
        ]):
            return bilgi

    # KAT BİLGİLERİ
    if "kat" in message_lower:
        for kat, bilgi in AVM_DATA["katlar"].items():
            if kat in message_lower:
                return f"{bilgi}"
        # Genel kat bilgisi
        return "\n".join([f"{k}: {v}" for k, v in AVM_DATA["katlar"].items()])

    # ÇALIŞMA SAATLERİ
    if any(word in message_lower for word in ["saat", "açık", "kapanış", "kaçta", "ne zaman"]):
        return f"AVM'miz her gün {AVM_DATA['saat']} saatleri arasında hizmet vermektedir."

    # MAĞAZALAR HAKKINDA
    for kategori, magazalar in AVM_DATA["mağazalar"].items():
        if kategori in message_lower:
            return f"{kategori.capitalize()} mağazalarımız: {', '.join(magazalar)}"

    # YEMEK SORGUSU
    if any(word in message_lower for word in ["restoran", "yemek", "kafe", "cafe", "yiyecek", "acıktım", "karnım aç"]):
        return f"Yemek katı 2. katta bulunuyor. Restoranlarımız arasında {', '.join(AVM_DATA['mağazalar']['restoran'])} bulunmaktadır."

    # Ne yemekler var sorusu için
    if "ne yemek" in message_lower or "hangi yemek" in message_lower or (
            "ne" in message_lower and "yemek" in message_lower):
        return f"Yemek katımızda şu restoranlar bulunmaktadır: {', '.join(AVM_DATA['mağazalar']['restoran'])}"

    # Genel AVM bilgisi
    if "avm" in message_lower:
        return f"{AVM_DATA['isim']} {AVM_DATA['kat_sayisi']} kattan oluşmaktadır. Çalışma saatlerimiz {AVM_DATA['saat']} arasındadır. Size nasıl yardımcı olabilirim?"

    # Varsayılan yanıt - daha spesifik bilgi isteyelim
    print("[DEBUG] Hiçbir özel kural eşleşmedi, varsayılan yanıt döndürülüyor")
    return "Mavi Vadi AVM asistanı olarak size yardımcı olmak için buradayım. Mağazalar, yemek alanları, sinema, eczane veya hastane hakkında bilgi verebilirim. Lütfen ne öğrenmek istediğinizi belirtin."