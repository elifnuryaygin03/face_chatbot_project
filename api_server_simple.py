from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API çalışıyor"}

@app.post("/recognize")
def recognize():
    return {"user_id": 999, "message": "Test kullanıcısı oluşturuldu"}

@app.post("/chat")
def chat(request: dict):
    return {"response": f"Mesajınız alındı: {request.get('message', '')}"}

@app.get("/chat_history/{user_id}")
def history(user_id: int):
    return []

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)