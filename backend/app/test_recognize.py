from face_utils import recognize_user

# Burada kesin dosya yolu veriyoruz, backend klasöründen başlatıyoruz
user_id = recognize_user(data_path="../data/known_faces.pkl")
print(f"Tanınan kullanıcı ID: {user_id}")