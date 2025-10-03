from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Basit API çalışıyor'}

if __name__ == '__main__':
    import uvicorn
    print("Uvicorn başlatılıyor...")
    uvicorn.run('simple_api:app', host='0.0.0.0', port=8889)
    print("Uvicorn tamamlandı.")  # Bu satır çalışırsa, sunucu normal kapandı demektir