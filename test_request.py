import requests
import json

# Load the payload from payload.json
with open("payload.json", "r") as f:
    payload = json.load(f)

BASE_URL = "https://pony-growing-tiger.ngrok-free.app/api/v1/hackrx/run"
HEADERS = {
    "Authorization": "Bearer 5fee3a33dca95ba5f96b0dba2b2115df43a00a7a874f6684b0c797b71e9aad58",
    "Content-Type": "application/json"
}

response = requests.post(BASE_URL, json=payload, headers=HEADERS)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())
