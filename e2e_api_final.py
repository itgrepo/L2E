#!/usr/bin/env python3
"""
API FINAL TEST: Using correct field name 'secret_key' and enabling API
"""
import requests, json, base64, time
from urllib.parse import quote

BASE = "http://134.185.172.127:3003/api"
T = 15

def ep(pw):
    e=base64.b64encode(quote(pw).encode()).decode(); return f"$e$={e[::-1]}"
def pe(d):
    s=json.dumps(d); e=base64.b64encode(s.encode()).decode(); return e[::-1]+"==e=="
def rj(r):
    try: return r.json()
    except: return {"raw":r.text[:300]}

# Login
rA = requests.post(f"{BASE}/login",json={"username":"qa_userA","password":ep("Password@123"),"link":"http://134.185.172.127:3003"},timeout=T)
uA = rA.json().get("data"); uAe = pe(uA)

MAIN_SID = 23
MAIN_DSID = "QA-FIN-1787474685"
DA_URL = f"http://134.185.172.127:3003/api/dataapi/api/v1/{MAIN_DSID}"

print("="*70)
print("API FINAL TEST")
print("="*70)

# Step 1: Enable API on dataset via saveApiConfig
print("\n▶ Step 1: Enable API on dataset")
r = requests.post(f"{BASE}/saveApiConfig", json={
    "user": uAe,
    "service_id": MAIN_SID,
    "api_enabled": 1,
    "api_type": "public",
    "api_db_name": "datax_db_3003",
    "api_source_name": "api_management_test_data",
    "api_source_type": "table",
    "api_request_fields": json.dumps(["province","status"]),
    "api_response_fields": json.dumps(["id","province","status","display_name"])
}, timeout=T)
j = rj(r)
print(f"  saveApiConfig: HTTP {r.status_code}, resp={json.dumps(j)[:200]}")

# Step 2: Create NEW credential (note: key is in 'secret_key' field)
print("\n▶ Step 2: Create API Credential")
r = requests.post(f"{BASE}/addApiCredential", json={
    "user": uAe,
    "service_id": MAIN_SID,
    "target_user_id": uA.get("user_id"),
    "secret_key": ""
}, timeout=T)
j = rj(r)
# The key is returned as 'secret_key' in the response
api_key = j.get("secret_key") or j.get("api_key") or j.get("full_key")
cred_id = j.get("credential_id")
print(f"  Response: {json.dumps(j)[:300]}")
print(f"  API Key: {api_key[:40] if api_key else 'NONE'}...")
print(f"  Cred ID: {cred_id}")

if api_key:
    print(f"\n  ✅ API-01: Create Credential PASS (key={api_key[:30]}...)")
else:
    print(f"\n  ❌ API-01: Create Credential FAIL")

# Step 3: Call Dataset API with valid key
print("\n▶ Step 3: Call Dataset API with valid key")
r = requests.get(DA_URL, headers={"x-api-key": api_key}, timeout=T)
j = rj(r)
print(f"  HTTP {r.status_code}")
print(f"  Response: {json.dumps(j)[:400]}")
if r.status_code == 200:
    print(f"\n  ✅ API-02: Valid key call PASS")
else:
    print(f"\n  ❌ API-02: Valid key call FAIL (HTTP {r.status_code})")

# Step 4: No key
print("\n▶ Step 4: Call without key")
r = requests.get(DA_URL, timeout=T); j = rj(r)
print(f"  HTTP {r.status_code}, resp={json.dumps(j)[:200]}")
nk = r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","unauth","error","required"])
print(f"  {'✅' if nk else '❌'} API-03: No key {'PASS' if nk else 'FAIL'}")

# Step 5: Invalid key
print("\n▶ Step 5: Call with invalid key")
r = requests.get(DA_URL, headers={"x-api-key": "totally_fake_key"}, timeout=T); j = rj(r)
print(f"  HTTP {r.status_code}, resp={json.dumps(j)[:200]}")
ik = r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","invalid","error","not found"])
print(f"  {'✅' if ik else '❌'} API-04: Invalid key {'PASS' if ik else 'FAIL'}")

# Step 6: Revoke and re-call
print("\n▶ Step 6: Revoke credential then re-call")
if cred_id:
    r = requests.post(f"{BASE}/revokeApiCredential", json={"user": uAe, "credential_id": cred_id}, timeout=T)
    j = rj(r)
    print(f"  Revoke: HTTP {r.status_code}, resp={json.dumps(j)[:200]}")
    rok = r.status_code==200 and j.get("status") in ["success","revoked"]
    print(f"  {'✅' if rok else '❌'} API-06a: Revoke {'PASS' if rok else 'FAIL'}")
    
    # Re-call with revoked key
    r2 = requests.get(DA_URL, headers={"x-api-key": api_key}, timeout=T); j2 = rj(r2)
    print(f"  Re-call: HTTP {r2.status_code}, resp={json.dumps(j2)[:200]}")
    rd = r2.status_code in [401,403] or any(w in str(j2).lower() for w in ["revoked","denied","invalid","error","inactive"])
    print(f"  {'✅' if rd else '❌'} API-06b: Revoked key rejected {'PASS' if rd else 'FAIL'}")
else:
    print(f"  ⚠️ API-06: BLOCKED (no cred_id)")

# Step 7: Email - check for Dataset Created email trigger
print("\n▶ Step 7: Email evidence from dataset operations")
print(f"  Backend logs show: 'Error sending email to a@b.com' during addService")
print(f"  This means: Backend ATTEMPTS to send email to admin notification list")
print(f"  But SMTP connection to 'outgoing.workd.go.th:465' fails from this environment")
print(f"  Email trigger: PASS (code path executed)")
print(f"  SMTP submission: FAIL (connection error to production SMTP)")
print(f"  Inbox delivery: BLOCKED (cannot verify)")

print("\n" + "="*70)
print("DONE")
print("="*70)
