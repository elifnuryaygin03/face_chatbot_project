from app.db import init_db  # db.py içindeki init_db fonksiyonunu içe aktarıyoruz

print("Veritabanı oluşturuluyor...")
init_db()
print("Veritabanı başarıyla oluşturuldu.")