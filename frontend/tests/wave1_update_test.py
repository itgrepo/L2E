import requests
import json
import base64
import time

BASE_URL = "http://134.185.172.127:3011"
admin_user_data = {"user_id": "1", "username": "admin", "previlage_id": "1"}
payload = json.dumps(admin_user_data)

def encode(payload):
    b64 = base64.b64encode(payload.encode()).decode()
    return b64[::-1] + "12345"

admin_token = encode(payload)

def test_update_pii():
    data = {
        "user": admin_token,
        "service_id": "20",
        "access_type": "restricted",
    }
    r = requests.put(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 200, f"Failed: {r.text}"
    print("test_update_pii: Passed", r.json())

if __name__ == "__main__":
    test_update_pii()
