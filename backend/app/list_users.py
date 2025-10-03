import sys
import os

# models.py ve db.py dosyaları bir üst klasörde (backend), orayı path'e ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), '..')))

from models import User              # Kullanıcı modelini içe aktar
from db import SessionLocal          # Veritabanı bağlantısı için session oluşturucu

# Veritabanına bağlan
db = SessionLocal()

# Tüm kullanıcıları çek
users = db.query(User).all()

# Her kullanıcıyı yazdır
if users:
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}")
else:
    print("Kayıtlı kullanıcı bulunamadı.")

# Bağlantıyı kapat
db.close()