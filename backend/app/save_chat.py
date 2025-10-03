# backend/app/save_chat.py
try:
    from app.db import SessionLocal
    from app.models import User, ChatHistory

    DB_AVAILABLE = True
    print("[INFO] Veritabanı modülleri başarıyla yüklendi.")
except ImportError as e:
    print(f"[WARNING] Veritabanı modülleri yüklenemedi: {e}")
    print("[WARNING] Test modu aktif: Veritabanı işlemleri simüle edilecek")
    DB_AVAILABLE = False


def save_message(user_id: int, message: str, is_bot: bool):
    """
    Mesajı veritabanına kaydeder.

    Args:
        user_id (int): Mesajı gönderen kullanıcının ID'si
        message (str): Mesaj içeriği
        is_bot (bool): Mesaj bot tarafından mı gönderildi? (True/False)
    """
    print(f"[INFO] Mesaj kaydediliyor: user_id={user_id}, is_bot={is_bot}, message='{message}'")

    if not DB_AVAILABLE:
        print("[TEST] Test modu: Veritabanı kaydı simüle ediliyor")
        return True

    try:
        db = SessionLocal()
        try:
            # Kullanıcı var mı kontrol et
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"[WARNING] ID {user_id} için kullanıcı bulunamadı. Test kullanıcısı oluşturuluyor.")
                user = User(id=user_id, name=f"User_{user_id}")
                db.add(user)
                db.commit()

            new_message = ChatHistory(
                user_id=user_id,
                message=message,
                is_user=0 if is_bot else 1
            )
            db.add(new_message)
            db.commit()
            print("[INFO] Mesaj başarıyla kaydedildi")
            return True
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Mesaj kaydedilirken hata oluştu: {e}")
            return False
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] Veritabanı bağlantısında hata: {e}")
        return False


def get_chat_history(user_id: int, limit: int = 20):
    """
    Kullanıcının önceki mesajlarını (hem kullanıcı hem bot mesajları) getirir.

    Args:
        user_id (int): Kullanıcı ID'si
        limit (int): En son kaç mesajı almak istediğimiz (varsayılan 20)

    Returns:
        List of ChatHistory objeleri veya test verisi
    """
    print(f"[INFO] Chat geçmişi getiriliyor: user_id={user_id}, limit={limit}")

    if not DB_AVAILABLE:
        print("[TEST] Test modu: Boş geçmiş döndürülüyor")
        return []

    try:
        db = SessionLocal()
        try:
            messages = (
                db.query(ChatHistory)
                .filter(ChatHistory.user_id == user_id)
                .order_by(ChatHistory.timestamp.desc())
                .limit(limit)
                .all()
            )
            print(f"[INFO] {len(messages)} mesaj bulundu")
            return messages[::-1]  # En eski mesaj önce gelsin diye ters çeviriyoruz
        except Exception as e:
            print(f"[ERROR] Geçmiş alınırken hata oluştu: {e}")
            return []
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] Veritabanı bağlantısında hata: {e}")
        return []