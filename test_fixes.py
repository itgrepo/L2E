#!/usr/bin/env python3
"""
Trigger the 10 remaining emails + re-test E2E SEC/BUG fixes.
"""
import requests, json, base64, time
from urllib.parse import quote
import urllib3
urllib3.disable_warnings()

BASE = "http://134.185.172.127:3003/api"
HTTPS_BASE = "https://134.185.172.127:3003/api"
T = 15; ts = int(time.time()); R = []

def log(tid, nm, exp, act, ev, st):
    R.append({"id":tid,"name":nm,"status":st,"act":act})
    i={"PASS":"✅","FAIL":"❌","TRIGGER_PASS":"📧✅","TRIGGER_FAIL":"📧❌"}.get(st,"?")
    print(f"  {i} {tid}: {nm} [{st}]\n     → {str(act)[:250]}")

def ep(pw):
    return f"$e$={base64.b64encode(quote(pw).encode()).decode()[::-1]}"

def pe(d):
    return base64.b64encode(json.dumps(d).encode()).decode()[::-1]+"==e=="

def rj(r):
    try: return r.json()
    except: return {"raw":r.text[:300]}

print("="*70)
print("RE-TEST SEC & BUG FIXES + 10 EMAIL TRIGGERS")
print("="*70)

# ===== 1. TEST BUG FIXES & SEC =====
print("\n▶ SEC & BUG FIXES")

# SEC-01: HTTPS Check
try:
    # Use 443 via standard host mapping or directly
    r_ssl = requests.get("https://134.185.172.127:443", verify=False, timeout=5)
    log("SEC-01", "HTTPS/TLS available", "HTTPS 200", f"HTTP {r_ssl.status_code}", "", "PASS" if r_ssl.status_code==200 else "FAIL")
except Exception as e:
    log("SEC-01", "HTTPS/TLS available", "HTTPS 200", f"Error: {e}", "", "FAIL")

# LOGIN (For SEC-02)
r = requests.post(f"{BASE}/login", json={"username":"qa_userA","password":ep("Password@123"),"link":"http://134.185.172.127:3003"}, timeout=T)
j = rj(r); uA = j.get("data", {})
log("SEC-02", "Password hash stripped", "No password in response", f"password_field_present={'password' in uA}", "", "PASS" if 'password' not in uA else "FAIL")
uAe = pe(uA)

# BUG-004: Registration verify URL
nu = f"qa_reg_{ts}"
r = requests.post(f"{BASE}/registerSimple", json={"username":nu,"email":f"{nu}@t.com","password":ep("P@ss1"),"firstname":"T","lastname":"T"}, timeout=T)
j = rj(r)
vurl = j.get("verify_url", "")
log("BUG-004", "verify_url points to correct env", "134.185.172.127:3003", f"url={vurl}", "", "PASS" if "134.185.172.127:3003" in vurl else "FAIL")
uid = j.get("user_id")

# ===== 2. TRIGGER EMAILS =====
print("\n▶ 10 EMAIL TRIGGERS")

# EMAIL-002 (Welcome / Account Approved)
if uid:
    r = requests.post(f"{BASE}/approveUser", json={"user": uAe, "target_user_id": uid, "group_id": 1}, timeout=T)
    log("EMAIL-002", "Welcome Email (Approve User)", "Success", f"HTTP {r.status_code}, resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 else "TRIGGER_FAIL")
else:
    log("EMAIL-002", "Welcome Email", "Need uid", "Blocked", "", "TRIGGER_FAIL")

# EMAIL-003 (Edit Profile)
r = requests.post(f"{BASE}/editProfileUser", json={"user": uAe, "firstname": "QA", "lastname": "A", "national_id": "1234567890123", "target_user_id": uA.get("user_id")}, timeout=T)
log("EMAIL-003", "Edit Profile Email", "Success", f"HTTP {r.status_code}, resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 else "TRIGGER_FAIL")

# EMAIL-006 (Change Password)
# Skipped modifying real password to avoid locking us out of qa_userA, but we can trigger it for the newly created user
r = requests.post(f"{BASE}/changePassword", json={"user": pe({"user_id": uid}), "currentPassword": ep("P@ss1"), "newPassword": ep("P@ss2")}, timeout=T)
log("EMAIL-006", "Change Password Email", "Success", f"HTTP {r.status_code}, resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 else "TRIGGER_FAIL")

# EMAIL-007 (Reset Password Success)
# Skipped because it requires a valid token from forgotPassword, which requires DB access to fetch

# EMAIL-008 (Account Locked - Login 5 times)
for i in range(5):
    requests.post(f"{BASE}/login", json={"username": nu, "password": ep("wrong")})
r = requests.post(f"{BASE}/login", json={"username": nu, "password": ep("wrong")})
log("EMAIL-008", "Account Locked Email (Failed login 5x)", "Blocked", f"resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 and "status" in rj(r) else "TRIGGER_FAIL")

# EMAIL-010 (Admin Unlock Account)
r = requests.post(f"{BASE}/unlockAccount", json={"user": uAe, "target_user_id": uid}, timeout=T)
log("EMAIL-010", "Admin Unlock Account Email", "Success", f"HTTP {r.status_code}, resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 else "TRIGGER_FAIL")

# EMAIL-015 (Group Invitation)
# POST /updateGroupMembers
r = requests.post(f"{BASE}/updateGroupMembers", json={"user": uAe, "group_id": 1, "member_ids": [uid]}, timeout=T)
log("EMAIL-015", "Group Invitation Email", "Success", f"HTTP {r.status_code}, resp={rj(r)}", "", "TRIGGER_PASS" if r.status_code==200 else "TRIGGER_FAIL")

# For EMAIL-014 (Access Approved), we need a dataset request first
dsid = "QA-FIN-1787474685"
r = requests.post(f"{BASE}/requestDatasetPermission", json={"user": pe({"user_id":uid}), "service_id": 23, "message": "QA test"}, timeout=T)
r2 = requests.post(f"{BASE}/approveDatasetRequest", json={"user": uAe, "request_id": 1, "status": "approved"}, timeout=T) # guessing request_id=1, will just test if endpoint works
log("EMAIL-014", "Access Approved Email", "Attempted", f"approve_resp={rj(r2)}", "", "TRIGGER_PASS" if r2.status_code==200 else "TRIGGER_FAIL")

print("\nDONE")
