from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import Optional
import shutil
import os
import face_recognition
import uvicorn

# Veritabanı ayarları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "chatbot.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"
print(f"[INFO] Veritabanı yolu: {DB_FILE}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    is_student = Column(Boolean, nullable=True)
    face_encoding = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age}, gender={self.gender}, is_student={self.is_student})>"


# Veritabanını oluştur
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("[INFO] Veritabanı tabloları başarıyla oluşturuldu")
    except Exception as e:
        print(f"[ERROR] Veritabanı tabloları oluşturulurken hata: {e}")


# Veritabanı bağlantısı için dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI uygulaması
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Yüz resimleri için klasör
UPLOAD_DIR = "uploaded_faces"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload/")
async def upload_face(file: UploadFile = File(...), user_id: str = Form(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, f"{user_id}.jpg")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = face_recognition.load_image_file(file_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        return {"error": "Yüz bulunamadı, lütfen başka bir fotoğraf deneyin."}

    user = db.query(User).filter(User.name == user_id).first()
    if not user:
        user = User(name=user_id)
        db.add(user)
        db.commit()

    return {"message": f"{user_id} için yüz kaydedildi.", "file_path": file_path, "user_id": user.id}


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


@app.post("/users/")
async def create_or_update_user(
        user_id: str = Form(...),
        age: Optional[int] = Form(None),
        gender: Optional[str] = Form(None),
        is_student: Optional[bool] = Form(None),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.name == user_id).first()

    if user:
        user.age = age
        user.gender = gender
        user.is_student = is_student
    else:
        user = User(
            name=user_id,
            age=age,
            gender=gender,
            is_student=is_student
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "user_id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender,
        "is_student": user.is_student
    }


@app.get("/users/{user_id}")
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    return {
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender,
        "is_student": user.is_student
    }


# Uygulama çalıştırma
if __name__ == "__main__":
    uvicorn.run("combined_app:app", host="0.0.0.0", port=9000, reload=True)