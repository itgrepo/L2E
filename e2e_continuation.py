#!/usr/bin/env python3
"""
CONTINUATION TEST: API Management, Delete, Authorization
Using service_id=23 (QA-FIN-*) from DB
"""
import requests, json, base64, time
from urllib.parse import quote

BASE = "http://134.185.172.127:3003/api"
T = 15; R = []

def log(tid,nm,exp,act,ev,st):
    R.append({"id":tid,"name":nm,"expected":exp,"actual":act,"evidence":ev,"status":st})
    i={"PASS":"✅","FAIL":"❌","BLOCKED":"⚠️","INFO":"ℹ️"}.get(st,"?")
    print(f"  {i} {tid}: {nm} [{st}]")
    if st in ("FAIL","BLOCKED"):
        print(f"     → Expected: {exp}")
        print(f"     → Actual:   {str(act)[:280]}")

def ep(pw):
    e=base64.b64encode(quote(pw).encode()).decode(); return f"$e$={e[::-1]}"
def pe(d):
    s=json.dumps(d); e=base64.b64encode(s.encode()).decode(); return e[::-1]+"==e=="
def rj(r):
    try: return r.json()
    except: return {"raw":r.text[:300]}

# Login both users
rA = requests.post(f"{BASE}/login",json={"username":"qa_userA","password":ep("Password@123"),"link":"http://134.185.172.127:3003"},timeout=T)
uA = rA.json().get("data"); uAe = pe(uA)
rB = requests.post(f"{BASE}/login",json={"username":"qa_userB","password":ep("Password@123"),"link":"http://134.185.172.127:3003"},timeout=T)
uB = rB.json().get("data"); uBe = pe(uB)

print(f"User A: id={uA.get('user_id')}, admin={uA.get('isAdmin')}")
print(f"User B: id={uB.get('user_id')}, admin={uB.get('isAdmin')}")

# Known service IDs from DB
MAIN_SID = 23     # QA-FIN-* dataset
MAIN_DSID = None  # Will find from retrieveService
DEL_SID = 25      # QA-DEL-* dataset

# Get exact dataset_id
r = requests.get(f"{BASE}/retrieveService", timeout=T)
for s in rj(r).get("data",[]):
    if s.get("service_id") == MAIN_SID:
        MAIN_DSID = s.get("dataset_id")
        print(f"Main dataset: service_id={MAIN_SID}, dataset_id={MAIN_DSID}, name={s.get('service_name')}")
        break

DA_URL = f"http://134.185.172.127:3003/api/dataapi/api/v1/{MAIN_DSID}"

print("\n" + "="*70)
print("CONTINUATION: API + DELETE + AUTHZ TESTS")
print("="*70)

# ===== DATASET EDIT =====
print("\n▶ DATASET EDIT\n")

ep_data = {
    "user": uAe,
    "service_id": MAIN_SID,
    "service_name": f"QA EDITED Dataset Final",
    "dataset_id": MAIN_DSID,
    "category": "Course Data",
    "organization": "Test",
    "source_system_id": "1",
    "access_type": "public",
    "accessibility": "Public",
    "service_status": "Active",
    "description": "EDITED by continuation test",
    "tags": "qa,edited",
    "contact_name": "QA Dept",
    "contact_email": "qa@test.com",
    "date_start": "2026-08-23",
    "date_updated": "2026-08-23"
}
r = requests.put(f"{BASE}/addService", data=ep_data, timeout=T); j = rj(r)
log("DS-EDIT-01","Edit dataset (User A admin)","Updated",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"sid={MAIN_SID}","PASS" if r.status_code==200 and "success" in str(j).lower() else "FAIL")

# Verify edit persisted
r = requests.get(f"{BASE}/retrieveService", timeout=T)
for s in rj(r).get("data",[]):
    if s.get("service_id") == MAIN_SID:
        log("DS-EDIT-02","Verify edit persisted","Name=QA EDITED",f"name={s.get('service_name')}, desc={s.get('description','')}","","PASS" if "EDITED" in str(s.get("service_name","")) else "FAIL")
        break

# User B edit User A's dataset
ep_b = dict(ep_data); ep_b["user"] = uBe; ep_b["service_name"] = "HACKED BY B"
r = requests.put(f"{BASE}/addService", data=ep_b, timeout=T); j = rj(r)
log("DS-EDIT-03","User B edit User A's dataset (authz)","Rejected 403",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")

# ===== API MANAGEMENT =====
print("\n▶ API MANAGEMENT\n")

# Create credential
r = requests.post(f"{BASE}/addApiCredential", json={
    "user": uAe, "service_id": MAIN_SID,
    "target_user_id": uA.get("user_id"), "secret_key": ""
}, timeout=T)
j = rj(r)
api_key = j.get("api_key") or j.get("full_key") or (j.get("credential",{}) or {}).get("full_key")
cred_id = j.get("credential_id") or (j.get("credential",{}) or {}).get("credential_id")
print(f"  → API Key created: {'YES' if api_key else 'NO'}, cred_id={cred_id}")
print(f"  → Full response: {json.dumps(j)[:300]}")
log("API-01","Create API Credential","Key returned",f"HTTP {r.status_code}, key={'YES' if api_key else 'NO'}, cred_id={cred_id}",f"key={api_key[:30] if api_key else 'NONE'}...","PASS" if api_key else "FAIL")

# Call API with valid key
if api_key:
    r = requests.get(DA_URL, headers={"x-api-key": api_key}, timeout=T); j = rj(r)
    log("API-02","Dataset API valid key","200 + data",f"HTTP {r.status_code}, resp={json.dumps(j)[:250]}","","PASS" if r.status_code==200 else "FAIL")
else:
    log("API-02","Dataset API valid key","Need key","No key returned","","BLOCKED")

# No key
r = requests.get(DA_URL, timeout=T); j = rj(r)
nk = r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","unauthorized","error","required","no api"])
log("API-03","Dataset API no key","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if nk else "FAIL")

# Invalid key
r = requests.get(DA_URL, headers={"x-api-key": "completely_fake_key_xyz"}, timeout=T); j = rj(r)
ik = r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","invalid","error","not found"])
log("API-04","Dataset API invalid key","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if ik else "FAIL")

# User B create credential (non-admin)
r = requests.post(f"{BASE}/addApiCredential", json={
    "user": uBe, "service_id": MAIN_SID,
    "target_user_id": uB.get("user_id"), "secret_key": ""
}, timeout=T)
j = rj(r)
log("API-05","User B create credential (non-admin)","Rejected 403",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")

# Revoke + re-call
if api_key and cred_id:
    r = requests.post(f"{BASE}/revokeApiCredential", json={"user": uAe, "credential_id": cred_id}, timeout=T)
    j = rj(r)
    log("API-06a","Revoke credential","Revoked",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"cid={cred_id}","PASS" if r.status_code==200 and j.get("status") in ["success","revoked"] else "FAIL")

    r2 = requests.get(DA_URL, headers={"x-api-key": api_key}, timeout=T); j2 = rj(r2)
    rd = r2.status_code in [401,403] or any(w in str(j2).lower() for w in ["revoked","denied","invalid","error","inactive"])
    log("API-06b","Call API after revoke","Rejected",f"HTTP {r2.status_code}, resp={json.dumps(j2)[:200]}","","PASS" if rd else "FAIL")
elif api_key:
    # Try getApiCredentials to find cred_id
    r = requests.post(f"{BASE}/getApiCredentials", json={"user": uAe, "service_id": MAIN_SID}, timeout=T)
    cj = rj(r)
    print(f"  → getApiCredentials response: {json.dumps(cj)[:300]}")
    
    # Try to extract cred_id
    creds = cj.get("credentials", cj.get("data", []))
    if isinstance(creds, list) and len(creds) > 0:
        cred_id = creds[-1].get("credential_id") or creds[-1].get("id")
        print(f"  → Found cred_id from list: {cred_id}")
        
        if cred_id:
            r = requests.post(f"{BASE}/revokeApiCredential", json={"user": uAe, "credential_id": cred_id}, timeout=T)
            j = rj(r)
            log("API-06a","Revoke credential","Revoked",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if j.get("status") in ["success","revoked"] else "FAIL")

            r2 = requests.get(DA_URL, headers={"x-api-key": api_key}, timeout=T); j2 = rj(r2)
            rd = r2.status_code in [401,403] or any(w in str(j2).lower() for w in ["revoked","denied","invalid","error","inactive"])
            log("API-06b","Call API after revoke","Rejected",f"HTTP {r2.status_code}, resp={json.dumps(j2)[:200]}","","PASS" if rd else "FAIL")
        else:
            log("API-06","Revoke test","Need cred_id","Cannot find in response","","BLOCKED")
    else:
        log("API-06","Revoke test","Need cred_id","Empty credentials list","","BLOCKED")
else:
    log("API-06","Revoke test","Need key+cred","Not available","","BLOCKED")

# ===== DELETE =====
print("\n▶ DATASET DELETE\n")

# Delete DEL dataset
r = requests.post(f"{BASE}/toggleServiceStatus", json={"user": uAe, "service_id": DEL_SID, "status": "Deleted"}, timeout=T)
j = rj(r)
log("DEL-01","Delete dataset (admin)","Deleted",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"sid={DEL_SID}","PASS" if r.status_code==200 else "FAIL")

# Check deleted dataset is gone from list
r = requests.get(f"{BASE}/retrieveService", timeout=T)
svc_list = rj(r).get("data",[])
still_active = any(s.get("service_id")==DEL_SID and s.get("status")=="Active" for s in svc_list)
log("DEL-02","Deleted dataset gone from active list","Not in active list",f"still_active={still_active}","","PASS" if not still_active else "FAIL")

# User B cannot delete User A's main dataset
r = requests.post(f"{BASE}/toggleServiceStatus", json={"user": uBe, "service_id": MAIN_SID, "status": "Deleted"}, timeout=T)
j = rj(r)
log("DEL-03","User B delete User A's dataset (authz)","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")

# ===== SUMMARY =====
print("\n" + "="*70)
print("CONTINUATION TEST SUMMARY")
print("="*70)
p=sum(1 for x in R if x["status"]=="PASS")
f=sum(1 for x in R if x["status"]=="FAIL")
b=sum(1 for x in R if x["status"]=="BLOCKED")
print(f"\n  Total: {len(R)}")
print(f"  ✅ PASS:    {p}")
print(f"  ❌ FAIL:    {f}")
print(f"  ⚠️  BLOCKED: {b}")

print("\n--- ALL ---\n")
for x in R:
    ic={"PASS":"✅","FAIL":"❌","BLOCKED":"⚠️","INFO":"ℹ️"}.get(x["status"],"?")
    print(f"  {ic} {x['id']:20s} {x['status']:10s} {x['name']}")
    print(f"     Act: {str(x['actual'])[:300]}")
    if x["evidence"]: print(f"     Ev:  {str(x['evidence'])[:300]}")
    print()
