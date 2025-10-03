import cv2
import face_recognition
import pickle
import os

# ✅ Proje kökünden 'data/known_faces.pkl' yolunu oluştur
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
ENCODINGS_PATH = os.path.join(BASE_DIR, "data", "known_faces.pkl")

def load_known_faces():
    """Var olan yüz verilerini dosyadan yükler."""
    if os.path.exists(ENCODINGS_PATH):
        with open(ENCODINGS_PATH, 'rb') as f:
            data = pickle.load(f)
            return data.get("encodings", []), data.get("user_ids", [])
    return [], []

def save_known_faces(encodings, user_ids):
    """Yüz verilerini dosyaya kaydeder."""
    os.makedirs(os.path.dirname(ENCODINGS_PATH), exist_ok=True)
    with open(ENCODINGS_PATH, 'wb') as f:
        pickle.dump({"encodings": encodings, "user_ids": user_ids}, f)

def register_user(user_id: int):
    """Yeni kullanıcıyı kameradan yüz tanıma ile kaydeder."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[HATA] Kamera açılamadı.")
        return

    print(f"[INFO] Kullanıcı {user_id} için yüz kaydı başlatıldı. Lütfen kameraya bakın...")

    encodings, user_ids = load_known_faces()
    added = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[HATA] Görüntü alınamadı.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if face_encodings:
            encodings.append(face_encodings[0])
            user_ids.append(user_id)
            added = True
            print(f"[✅] Kullanıcı {user_id} başarıyla kaydedildi.")
            break

        cv2.imshow("Kayıt için kameraya bakın - ESC ile çık", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            print("[⛔] Kayıt işlemi iptal edildi.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if added:
        save_known_faces(encodings, user_ids)
    else:
        print("[UYARI] Herhangi bir yüz kaydedilmedi.")

if __name__ == "__main__":
    try:
        user_id = int(input("Kaydedilecek kullanıcı ID'sini girin: "))
        register_user(user_id)
    except ValueError:
        print("[HATA] Lütfen geçerli bir sayı girin.")