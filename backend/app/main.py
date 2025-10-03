from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import face_recognition
import uvicorn
from db import SessionLocal, init_db
from models import User, ChatHistory

# Bilgi Yapısı
AVM_BILGILERI = {
    "eczane": "Giriş katında, sol tarafta. Saat 10:00 - 22:00 arası açık.",
    "hastane": "AVM'nin arka çıkışından 500 metre ileride, sağda.",
    "yemek katı": {
        "konum": "2. katta, merdivenleri çıktıktan sonra sağda.",
        "markalar": ["Fast Food A", "Restoran B", "Kafe C"]
    },
    "sinema": {
        "konum": "3. katta, asansörden inince sağda.",
        "filmler": [
            {"isim": "Film A", "saatler": ["12:00", "15:00", "18:00"]},
            {"isim": "Film B", "saatler": ["11:00", "14:00", "17:00"]},
            {"isim": "Film C", "saatler": ["13:00", "16:00", "19:00"]}
        ]
    },
    "market": "1. katta, giriş kapısının karşısında."
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_faces")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload/")
async def upload_face(file: UploadFile = File(...), user_id: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}.jpg")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = face_recognition.load_image_file(file_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        return {"error": "Yüz bulunamadı, lütfen başka bir fotoğraf deneyin."}

    return {"message": f"{user_id} için yüz kaydedildi.", "file_path": file_path}


@app.post("/recognize/")
async def recognize_face(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = os.path.join(UPLOAD_DIR, "temp.jpg")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    unknown_img = face_recognition.load_image_file(temp_path)
    unknown_encodings = face_recognition.face_encodings(unknown_img)
    if len(unknown_encodings) == 0:
        return {"error": "Yüz bulunamadı."}

    unknown_encoding = unknown_encodings[0]

    for saved_file in os.listdir(UPLOAD_DIR):
        if saved_file == "temp.jpg":
            continue

        saved_img = face_recognition.load_image_file(os.path.join(UPLOAD_DIR, saved_file))
        saved_encodings = face_recognition.face_encodings(saved_img)

        if len(saved_encodings) > 0:
            match = face_recognition.compare_faces([saved_encodings[0]], unknown_encoding)[0]

            if match:
                user_name = saved_file.replace(".jpg", "")
                user = db.query(User).filter(User.name == user_name).first()

                if user:
                    return {
                        "message": f"Hoş geldin, {user.name}!",
                        "user_id": user.id,
                        "name": user.name,
                        "age": user.age,
                        "gender": user.gender,
                        "is_student": user.is_student
                    }
                return {"message": f"Hoş geldin, {user_name}!", "user_name": user_name}

    return {"message": "Yüz tanınamadı."}


@app.post("/chat/{user_id}")
async def chat_with_user(user_id: int, message: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    chat = ChatHistory(user_id=user_id, message=message, is_user=True)
    db.add(chat)
    db.commit()

    response = f"{user.name}, '{message}' için şunları öneriyorum..."
    bot_response = ChatHistory(user_id=user_id, message=response, is_user=False)
    db.add(bot_response)
    db.commit()

    return {"response": response}


if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)