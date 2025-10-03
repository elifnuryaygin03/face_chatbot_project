import cv2
import face_recognition
import pickle
import os

def add_face(user_id: int, data_path="backend/data/known_faces.pkl"):
    print("[INFO] Kamera başlatılıyor...")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows için
    if not cap.isOpened():
        print("[ERROR] Kamera açılamadı.")
        return False

    known_faces = {
        "encodings": [],
        "user_ids": []
    }

    if os.path.exists(data_path):
        with open(data_path, "rb") as f:
            known_faces = pickle.load(f)

    print("[INFO] Yeni yüz kaydı için hazır. Kamera önüne geç ve 'q' ile kaydı başlat.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Kamera görüntüsü alınamadı.")
            continue

        cv2.imshow("Kayıt İçin Kamera (q tuşuna basarak kaydet)", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            if len(face_locations) != 1:
                print("[ERROR] Lütfen sadece bir yüz olacak şekilde kameranın önünde durun.")
                continue

            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            # Yeni yüzü listeye ekle
            known_faces["encodings"].append(face_encoding)
            known_faces["user_ids"].append(user_id)

            with open(data_path, "wb") as f:
                pickle.dump(known_faces, f)

            print(f"[INFO] Yüz başarıyla kaydedildi: User ID {user_id}")
            break

        elif key == 27:  # ESC tuşu ile çıkış
            print("[INFO] Kayıt iptal edildi.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Kullanım: python add_face.py <user_id>")
    else:
        user_id = int(sys.argv[1])
        add_face(user_id)