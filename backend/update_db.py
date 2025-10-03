import sqlite3
import os
import shutil
from datetime import datetime

# Veritabanı yolunu belirle
db_path = "chatbot.db"

# Yedek dosya yolu
backup_path = f"chatbot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print(f"Veritabanı yolu: {db_path}")

try:
    # Veritabanının var olduğundan emin olun
    if not os.path.exists(db_path):
        print("Veritabanı dosyası bulunamadı!")
        exit(1)

    # Veritabanı yedeği al
    print("Veritabanı yedeği alınıyor...")
    shutil.copy2(db_path, backup_path)
    print(f"Yedek oluşturuldu: {backup_path}")

    # Veritabanına bağlan
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users tablosunu kontrol et
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    print("Mevcut kolonlar:", column_names)

    # Gerekli kolonları ekle
    try:
        if "age" not in column_names:
            print("'age' kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER;")

        if "gender" not in column_names:
            print("'gender' kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT;")

        if "is_student" not in column_names:
            print("'is_student' kolonu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_student BOOLEAN;")

        # Değişiklikleri kaydet
        conn.commit()
        print("Veritabanı başarıyla güncellendi!")

    except Exception as e:
        conn.rollback()
        print(f"Veritabanı güncellenirken hata oluştu: {e}")

    # Tabloyu kontrol et
    cursor.execute("PRAGMA table_info(users)")
    updated_columns = cursor.fetchall()
    print("\nGüncellenen tablo yapısı:")
    for col in updated_columns:
        print(f"  {col[1]} ({col[2]})")

    # Bağlantıyı kapat
    conn.close()

except Exception as e:
    print(f"Hata: {e}")