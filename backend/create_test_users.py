import requests

data = {
    "user_id": "test_user",
    "name": "Elif",
    "age": 25,
    "gender": "K",
    "is_student": True
}

response = requests.post("http://127.0.0.1:9000/users/", data=data)
print(response.json())
