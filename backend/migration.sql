import os

# Örnek proje yapısı
project_structure = """
face_chatbot_project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── main.py
│   │   └── ...
│   ├── chatbot.db
│   └── migration.sql  # Bu dosyayı buraya koymalıyız
└── streamlit_app.py
"""

print(project_structure)

# Migration SQL kodunu oluştur
migration_sql = """-- Kullanıcı tablosunu yedekle
CREATE TABLE users_backup (
    id INTEGER PRIMARY KEY,
    name TEXT,
    face_encoding TEXT
);

-- Verileri yedek tabloya kopyala
INSERT INTO users_backup SELECT id, name, face_encoding FROM users;

-- Eski tabloyu sil
DROP TABLE users;

-- Yeni tabloyu oluştur
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT,
    is_student BOOLEAN,
    face_encoding TEXT
);

-- Verileri yeni tabloya kopyala (yeni alanlar NULL olacak)
INSERT INTO users (id, name, face_encoding)
SELECT id, name, face_encoding FROM users_backup;

-- Yedek tabloyu sil
DROP TABLE users_backup;
"""

# Tam konum örneği (gerçek yol sizin sisteminizdekine göre değişebilir)
example_path = r"C:\Users\elifn\Desktop\face_chatbot_project\backend\migration.sql"
print(f"\nDosyanın tam konumu örneği: {example_path}")

# Veritabanı güncelleme komutu
update_command = "sqlite3 chatbot.db < migration.sql"
print(f"\nVeri tabanını güncellemek için çalıştırmanız gereken komut (backend klasöründe): {update_command}")