from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Yeni eklendi
import sqlite3
import os
import time
from datetime import datetime
import json
from typing import List, Optional

app = FastAPI(title="AVM Chatbot API")

# CORS ayarları eklendi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm kaynaklara izin verir
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin verir
    allow_headers=["*"],  # Tüm başlıklara izin verir
)

# JSON kodlama ayarları
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

@app.middleware("http")
async def add_charset_middleware(request, call_next):
    response = await call_next(request)
    if isinstance(response, JSONResponse):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

# Veritabanı yapısı
DB_PATH = "avm_chatbot.db"

# AVM verileri
try:
    with open("avm_data.json", "r", encoding="utf-8") as f:
        AVM_DATA = json.load(f)
except Exception as e:
    print(f"AVM verileri yüklenirken hata: {e}")
    AVM_DATA = {
        "isim": "Mavi Vadi AVM",
        "saat": "10:00-22:00",
        "kat_sayisi": 5,
        "katlar": {
            "-1": "Otopark",
            "0": "Giriş Kat - Marketler ve Teknoloji",
            "1": "Giyim Katı",
            "2": "Yemek ve Sinema Katı",
            "3": "Çocuk ve Etkinlik Katı"
        },
        "yerler": {
            "eczane": "AVM'nin batı çıkışında 200 metre ileride. AVM'den çıktıktan sonra sağa dönüp 200 metre düz gitmeniz gerekiyor.",
            "hastane": "AVM'nin kuzeyinde 1 km mesafede. AVM'den çıkıp ana caddeye çıkın ve sola dönün. 10-15 dakikalık yürüme mesafesinde.",
            "yemek": "Yemek katı 2. katta bulunuyor. Asansör veya yürüyen merdivenlerle ulaşabilirsiniz.",
            "sinema": "Sinema 2. katta bulunuyor. Biletler gişeden veya mobil uygulamamızdan alınabilir."
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

# Veritabanını oluştur
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Kullanıcılar tablosu
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   """)
    # Mesajlar tablosu
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS messages
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       message
                       TEXT,
                       is_bot
                       BOOLEAN,
                       timestamp
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   )
                       )
                   """)
    conn.commit()
    conn.close()
    print("Veritabanı başarıyla oluşturuldu.")

# Model tanımları
class Message(BaseModel):
    user_id: int
    message: str

class ChatHistory(BaseModel):
    id: int
    message: str
    is_bot: bool
    timestamp: str

class User(BaseModel):
    id: int
    name: Optional[str] = None

class UserCreate(BaseModel):
    name: Optional[str] = None

def generate_response(message: str, user_id: int = None, user_name: str = None) -> str:
    """
    Kullanıcı mesajına yanıt üretir - Chatbot mantığı
    """
    # Mesajı küçük harfe çevir
    message_lower = message.lower()
    # İsim tanıma
    if ("adım" in message_lower or "ismim" in message_lower):
        words = message_lower.split()
        for i, word in enumerate(words):
            if word in ["adım", "ismim"]:
                if i + 1 < len(words):
                    update_user_name(user_id, words[i + 1].capitalize())
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
        # Genel kat bilgisi
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
    # GİYİM MAĞAZALARI SORGUSU
    if "giyim" in message_lower or "kıyafet" in message_lower or "elbise" in message_lower:
        if "nerede" in message_lower or "hangi kat" in message_lower:
            return "Giyim mağazaları 1. katta bulunmaktadır."
        else:
            return f"Giyim mağazalarımız: {', '.join(AVM_DATA['mağazalar']['giyim'])}. Bunlar 1. katta bulunmaktadır."
    # Genel AVM bilgisi
    if "avm" in message_lower:
        return f"{AVM_DATA['isim']} {AVM_DATA['kat_sayisi']} kattan oluşmaktadır. Çalışma saatlerimiz {AVM_DATA['saat']} arasındadır. Size nasıl yardımcı olabilirim?"
    # Varsayılan yanıt
    return "Mavi Vadi AVM asistanı olarak size yardımcı olmak için buradayım. Mağazalar, restoranlar, sinema, eczane veya diğer hizmetler hakkında bilgi verebilirim. Örneğin 'Hangi restoranlar var?', 'Sinemada hangi filmler oynuyor?' veya 'Eczaneye nasıl giderim?' gibi sorular sorabilirsiniz."

# Veritabanı işlemleri
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "name": user[1]}
    return None

def create_user(name=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if name:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    else:
        cursor.execute("INSERT INTO users DEFAULT VALUES")
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def update_user_name(user_id, name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    conn.commit()
    conn.close()

def save_message(user_id, message, is_bot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, message, is_bot) VALUES (?, ?, ?)",
                   (user_id, message, is_bot))
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, message, is_bot, timestamp
                   FROM messages
                   WHERE user_id = ?
                   ORDER BY timestamp DESC
                       LIMIT ?
                   """, (user_id, limit))
    messages = cursor.fetchall()
    conn.close()
    # Sonuçları ters çevir (en eskiden en yeniye)
    messages.reverse()
    return [{"id": m[0], "message": m[1], "is_bot": bool(m[2]), "timestamp": m[3]} for m in messages]

# API Endpoints
@app.get("/")
def root():
    return {"message": "AVM Chatbot API calisiyor", "status": "online"}

@app.post("/users", response_model=User)
def create_new_user(user: UserCreate):
    user_id = create_user(user.name)
    return {"id": user_id, "name": user.name}

@app.get("/users/{user_id}", response_model=User)
def get_user_info(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user

@app.put("/users/{user_id}")
def update_user_info(user_id: int, user: UserCreate):
    existing_user = get_user(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    update_user_name(user_id, user.name)
    return {"message": "Kullanıcı adı güncellendi", "user_id": user_id, "name": user.name}

@app.post("/chat")
def chat(message: Message):
    user_id = message.user_id
    user_message = message.message
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    # Kullanıcı mesajını kaydet
    save_message(user_id, user_message, False)
    # Yanıt oluştur
    bot_response = generate_response(user_message, user_id, user.get("name"))
    # Bot yanıtını kaydet
    save_message(user_id, bot_response, True)
    return {"response": bot_response}

@app.get("/chat_history/{user_id}")
def get_history(user_id: int, limit: int = 20):
    history = get_chat_history(user_id, limit)
    return history

@app.post("/recognize")
def recognize_user():
    """
    Bu endpoint gerçek yüz tanımayı simüle eder.
    Gerçek uygulamada, bir kamera görüntüsü alıp işleyebilirsiniz.
    """
    # Yeni kullanıcı oluştur
    user_id = create_user()
    # Gerçek uygulamada, tanınan kullanıcı varsa onu döndürün
    return {"user_id": user_id, "message": "Kullanıcı tanındı."}

@app.get("/test_tts")
def test_tts():
    """
    Text-to-Speech API test endpoint'i
    """
    return {
        "text": "Merhaba, ben Mavi Vadi AVM asistanıyım. Size nasıl yardımcı olabilirim?",
        "audio_url": "/static/test_audio.mp3"
    }

# Uygulama başlatılırken veritabanını oluştur
@app.on_event("startup")
async def startup_db_client():
    init_db()

if __name__ == "__main__":
    import uvicorn
    # Veritabanını başlat
    init_db()
    print("API sunucusu başlatılıyor...")
    uvicorn.run("api_server:app", host="0.0.0.0", port=9000)