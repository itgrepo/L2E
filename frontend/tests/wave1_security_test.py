import requests
import json
import base64
import time

BASE_URL = "http://134.185.172.127:3011"

admin_user_data = {"user_id": "1", "previlage_id": "1"}
admin_token = base64.b64encode(json.dumps(admin_user_data).encode()).decode()

def test_save_public():
    data = {
        "user": admin_token,
        "service_name": f"Test Public {time.time()}",
        "access_type": "public",
        "category": "Learning Catalog", # Valid
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)" # Now valid
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 200, f"Failed: {r.text}"
    assert "success" in r.json().get("status", "")

def test_invalid_access_type():
    data = {
        "user": admin_token,
        "service_name": f"Test Invalid {time.time()}",
        "access_type": "unknown",
        "category": "Learning Catalog",
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)"
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 400
    assert "Invalid access_type" in r.json().get("status", "")

def test_invalid_category():
    data = {
        "user": admin_token,
        "service_name": f"Test Invalid Cat {time.time()}",
        "access_type": "public",
        "category": "FakeCategory",
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)"
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 400
    assert "Category 'FakeCategory' not found" in r.json().get("status", "")

if __name__ == "__main__":
    try:
        test_save_public()
        test_invalid_access_type()
        test_invalid_category()
        print("Wave 1 Tests passed successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
