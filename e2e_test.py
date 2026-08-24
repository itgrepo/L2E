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

def register(username, email, password):
    url = f"{BASE_URL}/registerSimple"
    payload = {
        "username": username,
        "email": email,
        "password": encode_password(password),
        "firstname": "Test",
        "lastname": "User",
        "organization": "Test Org"
    }
    r = requests.post(url, json=payload)
    return r.json()

def login(username, password):
    url = f"{BASE_URL}/login"
    payload = {
        "username": username,
        "password": encode_password(password),
        "link": "http://134.185.172.127:3003"
    }
    r = requests.post(url, json=payload)
    return r.json()

print("Testing Registration...")
reg_res = register("qa_userA", "qa_userA@example.com", "Password@123")
print("Register User A:", reg_res)

reg_res = register("qa_userB", "qa_userB@example.com", "Password@123")
print("Register User B:", reg_res)

print("Testing Login...")
log_resA = login("qa_userA", "Password@123")
print("Login User A:", log_resA)

print("Testing Invalid Login...")
log_invalid = login("qa_userA", "WrongPass")
print("Login Invalid:", log_invalid)
