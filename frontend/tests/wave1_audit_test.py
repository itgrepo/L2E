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

def test_api_log():
    # Hit data API for the PII dataset we created earlier (dataset_id='PII_1785336282')
    # Actually wait, the PII dataset we created earlier didn't have data source config set up, 
    # so `get_dataset_api` will return 404 because `api_enabled` is 0 or it might fail because no table exists.
    # Let's see what it returns.
    r = requests.get(f"{BASE_URL}/dataapi/api/v1/PII_1785336282", headers={"x-api-key": "FAKE_KEY"})
    print("test_api_log:", r.status_code, r.text)

if __name__ == "__main__":
    test_api_log()
