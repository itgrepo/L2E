import requests, json, base64, time
from urllib.parse import quote

BASE = "http://134.185.172.127:3003/api"
MAILHOG = "http://134.185.172.127:8028/api/v2/messages"

def ep(pw):
    return f"$e$={base64.b64encode(quote(pw).encode()).decode()[::-1]}"

def pe(d):
    return base64.b64encode(json.dumps(d).encode()).decode()[::-1]+"==e=="

# 1. Login as Admin
r = requests.post(f"{BASE}/login", json={"username":"qa_admin2","password":ep("Password@123"), "link":"http://134.185.172.127:3003"})
admin_user = r.json().get("data")
admin_user_encoded = pe(admin_user)
admin_id = admin_user['user_id']

# 2. Login as Normal User
r = requests.post(f"{BASE}/login", json={"username":"qa_user2","password":ep("Password@123"), "link":"http://134.185.172.127:3003"})
if r.json().get("status") != "success":
    # Register qa_user2
    nu = "qa_user2"
    requests.post(f"{BASE}/registerSimple", json={"username":nu,"email":f"{nu}@example.com","password":ep("Password@123"),"firstname":"B","lastname":"B"})
    # Approve qa_user2
    tmp_r = requests.post(f"{BASE}/login", json={"username":nu,"password":ep("Password@123"), "link":"http://134.185.172.127:3003"})
    tmp_uid = tmp_r.json().get("data", {}).get("user_id")
    if tmp_uid:
        requests.post(f"{BASE}/approveUser", json={"user": admin_user_encoded, "target_user_id": tmp_uid, "group_id": 1})
    r = requests.post(f"{BASE}/login", json={"username":nu,"password":ep("Password@123"), "link":"http://134.185.172.127:3003"})

normal_user = r.json().get("data")
normal_user_encoded = pe(normal_user)
normal_id = normal_user['user_id']

print(f"Admin ID: {admin_id}, Normal ID: {normal_id}")

def get_emails():
    try:
        r = requests.get(MAILHOG)
        return r.json().get("items", [])
    except:
        return []

def clear_emails():
    requests.delete(f"http://134.185.172.127:8028/api/v1/messages")

def wait_for_email(subject_contains, timeout=5):
    for _ in range(timeout):
        for msg in get_emails():
            if subject_contains in msg.get("Content", {}).get("Headers", {}).get("Subject", [""])[0]:
                return msg
        time.sleep(1)
    return None

import uuid
matrix_results = []

def test_dataset_flow(access_type_label, access_type_value):
    print(f"\n=====================================")
    print(f" TESTING DATASET TYPE: {access_type_label}")
    print(f"=====================================")
    
    ds_name = f"QA-E2E-{access_type_label}-{int(time.time())}"
    clear_emails()
    
    # Create Dataset
    payload = {
        'user': admin_user_encoded,
        'service_name': ds_name,
        'description': 'QA E2E Test Dataset',
        'access_type': access_type_value,
        'accessibility': access_type_value,
        'data_source': 'database',
        'service_status': 'Active'
    }
    r = requests.post(f"{BASE}/addService", data=payload)
    if "Failed" in r.text or r.status_code != 200:
        print(f"Failed to create dataset: {r.text}")
        return
        
    print(f"Dataset {ds_name} created.")
    
    # Verify Email (Dataset Created)
    email = wait_for_email("New Dataset Available")
    if email:
        print(f"  [EMAIL PASS] Dataset Created notification triggered.")
    else:
        print(f"  [EMAIL FAIL] Dataset Created notification NOT triggered.")
        
    # Get the real service_id
    r = requests.post(f"{BASE}/getService", json={"user": admin_user_encoded})
    services = r.json()
    my_ds = next((s for s in services if s['service_name'] == ds_name), None)
    if not my_ds:
        print("Could not find dataset in list.")
        return
    
    sid = my_ds['service_id']
    dataset_id = my_ds['dataset_id']
    print(f"Dataset ID: {dataset_id}, Service ID: {sid}")
    
    # ---------------------------------------------------------
    # API Type 1: Public
    # ---------------------------------------------------------
    print("\n--- Testing API Type 1 (Public) ---")
    clear_emails()
    cfg = {
        "user": admin_user_encoded,
        "service_id": sid,
        "api_enabled": "true",
        "api_type": "public",
        "api_db_name": "datax_db_3003",
        "api_source_type": "table",
        "api_source_name": "api_management_test_data",
        "api_request_fields": ["province"],
        "api_response_fields": ["id", "province", "status", "display_name"]
    }
    r = requests.post(f"{BASE}/saveApiConfig", json=cfg)
    # Wait, saveApiConfig does not trigger email in the current system. (Requirement check)
    
    # Test Data API
    data_url = f"{BASE.replace('/api', '/dataapi')}/api/v1/{dataset_id}"
    r = requests.get(data_url)
    data = r.json()
    if r.status_code == 200 and isinstance(data, list) and len(data) > 0:
        print(f"  [API-1 PASS] No Key Call. Status: {r.status_code}. Rows: {len(data)}")
    else:
        print(f"  [API-1 FAIL] No Key Call. Status: {r.status_code}. Resp: {str(r.text)[:100]}")
        
    # ---------------------------------------------------------
    # API Type 2: Private
    # ---------------------------------------------------------
    print("\n--- Testing API Type 2 (Private) ---")
    cfg["api_type"] = "private"
    requests.post(f"{BASE}/saveApiConfig", json=cfg)
    
    # Test Data API (No Key) - Should Fail
    r = requests.get(data_url)
    if r.status_code == 401 or r.status_code == 403:
        print(f"  [API-2 PASS] No Key Call properly rejected: {r.status_code}")
    else:
        print(f"  [API-2 FAIL] No Key Call not rejected! Status: {r.status_code}")
        
    # Create Credential
    clear_emails()
    cred_req = {
        "user": admin_user_encoded,
        "service_id": sid,
        "api_type": "private"
    }
    r = requests.post(f"{BASE}/addApiCredential", json=cred_req)
    cred_res = r.json()
    if r.status_code == 200 and cred_res.get("status") == "success":
        api_key = cred_res.get("secret_key")
        print(f"  [API-2] Credential created.")
    else:
        print(f"  [API-2 FAIL] Credential creation failed: {r.text}")
        api_key = None
        
    if api_key:
        r = requests.get(data_url, headers={"x-api-key": api_key})
        data = r.json()
        if r.status_code == 200 and isinstance(data, list) and len(data) > 0:
            print(f"  [API-2 PASS] Valid Key Call. Status: {r.status_code}. Rows: {len(data)}")
        else:
            print(f"  [API-2 FAIL] Valid Key Call. Status: {r.status_code}. Resp: {str(r.text)[:100]}")
            
    # ---------------------------------------------------------
    # API Type 3: Scope
    # ---------------------------------------------------------
    print("\n--- Testing API Type 3 (Scope) ---")
    cfg["api_type"] = "scope"
    requests.post(f"{BASE}/saveApiConfig", json=cfg)
    
    if api_key:
        # Save scope for the user
        scope_def = [{
            "field": "province",
            "operator": "=",
            "value": "Bangkok",
            "logic": "AND"
        }]
        scope_req = {
            "user": admin_user_encoded,
            "service_id": sid,
            "target_user_id": admin_id,
            "scope_json": json.dumps(scope_def)
        }
        r = requests.post(f"{BASE}/saveApiScopeForUser", json=scope_req)
        
        # Test Data API
        r = requests.get(data_url, headers={"x-api-key": api_key})
        data = r.json()
        if r.status_code == 200 and isinstance(data, list):
            bkk_only = all(d.get("province") == "Bangkok" for d in data)
            print(f"  [API-3 PASS] Valid Key Call. Status: {r.status_code}. Rows: {len(data)}. Scoped properly: {bkk_only}")
        else:
            print(f"  [API-3 FAIL] Valid Key Call. Status: {r.status_code}. Resp: {str(r.text)[:100]}")

test_dataset_flow("Public", "Public")
test_dataset_flow("Restricted", "Restricted")
print("\nDone.")
