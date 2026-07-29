import requests
import json
import base64
import time
import sys

BASE_URL = "http://134.185.172.127:3011"

admin_user_data = {"user_id": "1", "username": "admin", "previlage_id": "1"}
payload = json.dumps(admin_user_data)

def encode(payload):
    b64 = base64.b64encode(payload.encode()).decode()
    return b64[::-1] + "12345"

admin_token = encode(payload)

def test_save_public():
    data = {
        "user": admin_token,
        "service_name": f"Test Public {time.time()}",
        "access_type": "public",
        "category": "Learning Catalog", # Valid
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)" # Valid
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 200, f"Failed: {r.text}"
    assert "success" in r.json().get("status", "")
    print("test_save_public: Passed")

def test_invalid_access_type():
    data = {
        "user": admin_token,
        "service_name": f"Test Invalid {time.time()}",
        "access_type": "unknown",
        "category": "Learning Catalog",
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)"
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "Invalid access_type" in r.json().get("status", "")
    print("test_invalid_access_type: Passed")

def test_invalid_category():
    data = {
        "user": admin_token,
        "service_name": f"Test Invalid Cat {time.time()}",
        "access_type": "public",
        "category": "FakeCategory",
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)"
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "not found" in r.json().get("status", "")
    print("test_invalid_category: Passed")

if __name__ == "__main__":
    try:
        test_save_public()
        test_invalid_access_type()
        test_invalid_category()
        print("Wave 1 Tests passed successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
