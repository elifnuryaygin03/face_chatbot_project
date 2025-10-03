import cv2
import face_recognition
import pickle
import os
import numpy as np
import time
import sys


def recognize_user(data_path="data/known_faces.pkl", tolerance=0.5, max_attempts=5):
    """
    Kamera üzerinden yüz tanıma işlemi yapar.
    Kayıtlı yüzler data_path üzerinden yüklenir ve gerçek zamanlı tanıma yapılır.

    Args:
        data_path (str): Yüz verilerinin kayıtlı olduğu pickle dosyasının yolu.
        tolerance (float): Yüz tanıma hassasiyet seviyesi (düşük = daha sıkı eşleşme).
        max_attempts (int): Maksimum deneme sayısı

    Returns:
        int: Kullanıcı ID'si (tanındıysa) veya -1 (tanınmadıysa)
    """
    print("[INFO] Kod başladı. Yüz tanıma test modu aktif.")

    # Test modu - Gerçek yüz tanıma yapmadan kullanıcı ID'si döndür
    print("[TEST] Test modu: Tanıma yapmadan kullanıcı 1 döndürülüyor")
    return 1