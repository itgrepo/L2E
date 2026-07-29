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
service_name = f"Test PII {time.time()}"

def test_save_pii():
    data = {
        "user": admin_token,
        "service_name": service_name,
        "access_type": "pii",
        "category": "Learning Catalog", 
        "organization": "สำนักงานปลัดกระทรวง พม. (OPS)",
        "dataset_id": f"PII_{int(time.time())}"
    }
    r = requests.post(f"{BASE_URL}/addService", data=data)
    assert r.status_code == 200, f"Failed: {r.text}"
    print("test_save_pii: Passed", r.json())
    return data["dataset_id"]

if __name__ == "__main__":
    dataset_id = test_save_pii()
    print("DATASET_ID:", dataset_id)
    print("SERVICE_NAME:", service_name)
