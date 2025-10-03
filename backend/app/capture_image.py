# capture_image.py
import cv2

def capture_image(user_id):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı.")
        return

    print("Kameradan görüntü alınıyor. 'SPACE' ile fotoğraf çek, 'ESC' ile çık.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Görüntü alınamadı.")
            break

        cv2.imshow("Fotoğraf Çekimi", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            image_path = f"backend/data/user{user_id}.jpg"
            cv2.imwrite(image_path, frame)
            print(f"Fotoğraf kaydedildi: {image_path}")
            break

    cap.release()
    cv2.destroyAllWindows()