import requests
import json
import base64
import time
from urllib.parse import quote

BASE_URL = "http://134.185.172.127:3003/api"

def encode_password(pwd):
    encoded = base64.b64encode(quote(pwd).encode('utf-8')).decode('utf-8')
    reversed_b64 = encoded[::-1]
    return f"$e$={reversed_b64}"

def platform_encode(data_str):
    encoded = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
    reversed_b64 = encoded[::-1]
    return reversed_b64 + "==e=="

def login(username, password):
    url = f"{BASE_URL}/login"
    payload = {
        "username": username,
        "password": encode_password(password),
        "link": "http://134.185.172.127:3003"
    }
    r = requests.post(url, json=payload)
    return r.json()

print("Login User A...")
userA = login("qa_userA", "Password@123")
print("User A Login Status:", userA.get('status'))
userA_data = userA.get('data')
userA_encoded = platform_encode(json.dumps(userA_data))

print("\nLogin User B...")
userB = login("qa_userB", "Password@123")
print("User B Login Status:", userB.get('status'))
userB_data = userB.get('data')
userB_encoded = platform_encode(json.dumps(userB_data))

print("\n--- Test Dataset Creation (User A) ---")
ds_payload = {
    "user": userA_encoded,
    "service_name": "Test Dataset A",
    "dataset_id": "TD-001",
    "category": "Test Category",
    "description": "Test E2E Dataset",
    "accessibility": "Public",
    "service_status": "Active"
}
r_ds = requests.post(f"{BASE_URL}/addService", data=ds_payload)
try:
    print("Add Dataset Response:", r_ds.json())
except:
    print("Add Dataset Response:", r_ds.text)

print("\n--- Test Dataset Creation Unauthorized (User B) ---")
ds_payload_b = {
    "user": userB_encoded,
    "service_name": "Test Dataset B",
    "dataset_id": "TD-002"
}
r_ds_b = requests.post(f"{BASE_URL}/addService", data=ds_payload_b)
try:
    print("Add Dataset User B Response:", r_ds_b.json())
except:
    print("Add Dataset User B Response (Status %s):" % r_ds_b.status_code, r_ds_b.text)
