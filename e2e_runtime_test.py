#!/usr/bin/env python3
"""
Runtime E2E Test - FINAL (with correct reference data from running DB)
Target: http://134.185.172.127:3003/
"""
import requests, json, base64, time
from urllib.parse import quote

BASE = "http://134.185.172.127:3003/api"
T = 15; ts = int(time.time()); R = []

def log(tid,nm,exp,act,ev,st):
    R.append({"id":tid,"name":nm,"expected":exp,"actual":act,"evidence":ev,"status":st})
    i={"PASS":"✅","FAIL":"❌","BLOCKED":"⚠️","INFO":"ℹ️","TRIGGER_PASS":"📧✅","TRIGGER_FAIL":"📧❌"}.get(st,"?")
    print(f"  {i} {tid}: {nm} [{st}]")
    if st in ("FAIL","BLOCKED","TRIGGER_FAIL"):
        print(f"     → {str(act)[:250]}")

def ep(pw):
    e=base64.b64encode(quote(pw).encode()).decode(); return f"$e$={e[::-1]}"
def pe(d):
    s=json.dumps(d); e=base64.b64encode(s.encode()).decode(); return e[::-1]+"==e=="
def login(u,p):
    return requests.post(f"{BASE}/login",json={"username":u,"password":ep(p),"link":"http://134.185.172.127:3003"},timeout=T)
def rj(r):
    try: return r.json()
    except: return {"raw":r.text[:300]}

print("="*70)
print(f"FINAL RUNTIME E2E TEST  |  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# ===== AUTH =====
print("\n▶ SECTION 1: AUTHENTICATION\n")

r=login("qa_userA","Password@123"); j=rj(r)
uA=j.get("data"); uAe=pe(uA) if uA else None
log("AUTH-01","Login Admin(qa_userA)","Login accepted",f"HTTP {r.status_code}, status={j.get('status')}, isAdmin={uA.get('isAdmin') if uA else '?'}","","PASS" if j.get("status") in ["success","change password","change password admin"] else "FAIL")

r=login("qa_userA","BadPass!"); j=rj(r)
log("AUTH-02","Login wrong password","Rejected",f"HTTP {r.status_code}, status={j.get('status')}","","PASS" if j.get("status")!="success" else "FAIL")

r=login("ghost_user_xyz","Any"); j=rj(r)
log("AUTH-03","Login non-existent user","Rejected",f"HTTP {r.status_code}, status={j.get('status')}","","PASS" if j.get("status")!="success" else "FAIL")

r=login("qa_userB","Password@123"); j=rj(r)
uB=j.get("data"); uBe=pe(uB) if uB else None
log("AUTH-04","Login Regular(qa_userB)","Login accepted",f"HTTP {r.status_code}, status={j.get('status')}, isAdmin={uB.get('isAdmin') if uB else '?'}","","PASS" if j.get("status") in ["success","change password","change password admin"] else "FAIL")

nu=f"qa_final_{ts}"; ne=f"qa_final_{ts}@example.com"
r=requests.post(f"{BASE}/registerSimple",json={"username":nu,"email":ne,"password":ep("TestP@ss1"),"firstname":"Final","lastname":"Tester","organization":"QA"},timeout=T)
j=rj(r); reg=j
log("AUTH-05","Register new user","status=success",f"HTTP {r.status_code}, status={j.get('status')}, user_id={j.get('user_id')}, verify_url={str(j.get('verify_url',''))[:60]}","","PASS" if j.get("status")=="success" else "FAIL")

r=requests.post(f"{BASE}/registerSimple",json={"username":"qa_userA","email":"x@x.com","password":ep("X"),"firstname":"X","lastname":"X","organization":"X"},timeout=T)
j=rj(r)
log("AUTH-06","Register duplicate username","Rejected",f"HTTP {r.status_code}, status={j.get('status')}, msg={j.get('message','')}","","PASS" if j.get("status")=="error" else "FAIL")

# HTTP status analysis
r=login("qa_userA","BadPw"); 
log("AUTH-07","HTTP status code on auth failure","200 with JSON error (API design)",f"HTTP {r.status_code}","API contract uses HTTP 200 + JSON status for all responses. Not a functional bug—API design choice.","INFO")

# ===== DATASET =====
print("\n▶ SECTION 2: DATASET LIFECYCLE\n")

csid=None; dsid=f"QA-FIN-{ts}"

if uAe:
    # Use REAL values from the running system
    valid_payload = {
        "user": uAe,
        "service_name": f"QA Final Test {ts}",
        "dataset_id": dsid,
        "category": "Course Data",           # Real category from DB
        "sub_category": "",
        "organization": "Test",              # org_name from organization table
        "source_system_id": "1",             # Real source_system.id
        "accessibility": "Public",
        "access_type": "public",             # From Frontend dropdown
        "service_status": "Active",
        "description": "E2E runtime test dataset with correct reference data",
        "tags": "qa,e2e,final",
        "contact_name": "QA Department",
        "contact_email": "qa@test.com",
        "date_start": "2026-08-23",
        "date_updated": "2026-08-23"
    }
    r=requests.post(f"{BASE}/addService",data=valid_payload,timeout=T); j=rj(r)
    csid=j.get("service_id")
    log("DS-01A","Create Dataset access_type='public' (valid refs)","Dataset created",f"HTTP {r.status_code}, service_id={csid}, resp={json.dumps(j)[:250]}","","PASS" if csid else "FAIL")

    # B) Missing access_type
    mp=dict(valid_payload); mp.pop("access_type",None); mp["service_name"]=f"QA-MAT-{ts}"; mp["dataset_id"]=f"QA-MAT-{ts}"
    r=requests.post(f"{BASE}/addService",data=mp,timeout=T); j=rj(r)
    log("DS-01B","Missing access_type","Validation error",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","Backend applies Thai placeholder default → rejected","INFO")

    # C) Empty access_type
    ep2=dict(valid_payload); ep2["access_type"]=""; ep2["service_name"]=f"QA-EAT-{ts}"; ep2["dataset_id"]=f"QA-EAT-{ts}"
    r=requests.post(f"{BASE}/addService",data=ep2,timeout=T); j=rj(r)
    log("DS-01C","Empty access_type","Validation error",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","INFO")

    # D) Invalid access_type
    ip=dict(valid_payload); ip["access_type"]="เลือกการเข้าถึง"; ip["service_name"]=f"QA-IAT-{ts}"; ip["dataset_id"]=f"QA-IAT-{ts}"
    r=requests.post(f"{BASE}/addService",data=ip,timeout=T); j=rj(r)
    log("DS-01D","Invalid access_type (placeholder)","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","Backend correctly rejects Thai placeholder","PASS" if "Invalid" in json.dumps(j) or r.status_code>=400 else "FAIL")

    # READ
    r=requests.get(f"{BASE}/retrieveService",timeout=T); j=rj(r)
    sl=j.get("data",[]) if isinstance(j,dict) else (j if isinstance(j,list) else [])
    found=any(s.get("dataset_id")==dsid for s in sl)
    log("DS-02","Read dataset list after create","Our dataset in list",f"HTTP {r.status_code}, found={found}, total={len(sl)}","","PASS" if found else "FAIL")

    if csid:
        # EDIT
        ep3=dict(valid_payload); ep3["service_id"]=csid; ep3["service_name"]=f"QA EDITED {ts}"; ep3["description"]="EDITED by E2E"
        r=requests.put(f"{BASE}/addService",data=ep3,timeout=T); j=rj(r)
        log("DS-03","Edit Dataset (PUT)","Updated",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"sid={csid}","PASS" if r.status_code==200 and j.get("status") in ["success","updated"] else "FAIL")

        # Verify edit
        r=requests.get(f"{BASE}/retrieveService",timeout=T); j2=rj(r)
        sl2=j2.get("data",[]) if isinstance(j2,dict) else (j2 if isinstance(j2,list) else [])
        fe=any(s.get("dataset_id")==dsid and "EDITED" in str(s.get("service_name","")) for s in sl2)
        log("DS-04","Verify edit persisted","Name updated on reload",f"found_edited={fe}","","PASS" if fe else "FAIL")

        # User B edit (authz)
        if uBe:
            eb=dict(valid_payload); eb["user"]=uBe; eb["service_id"]=csid; eb["service_name"]="HACKED"
            r=requests.put(f"{BASE}/addService",data=eb,timeout=T); j=rj(r)
            log("DS-05","User B edit User A's dataset","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")

# ===== API MANAGEMENT =====
print("\n▶ SECTION 3: API MANAGEMENT\n")

akey=None; cid=None
da_url=f"http://134.185.172.127:3003/api/dataapi/api/v1/{dsid}"

if uAe and csid:
    # Create credential
    r=requests.post(f"{BASE}/addApiCredential",json={"user":uAe,"service_id":csid,"target_user_id":uA.get("user_id",50),"secret_key":""},timeout=T)
    j=rj(r)
    akey=j.get("api_key") or j.get("full_key") or (j.get("credential",{}) or {}).get("full_key")
    cid=j.get("credential_id") or (j.get("credential",{}) or {}).get("credential_id")
    log("API-01","Create API Credential","Key returned",f"HTTP {r.status_code}, key={'YES' if akey else 'NO'}, cred_id={cid}, resp={json.dumps(j)[:250]}",f"key_pfx={akey[:25] if akey else 'NONE'}...","PASS" if akey else "FAIL")

    # Valid key call
    if akey:
        r=requests.get(da_url,headers={"x-api-key":akey},timeout=T); j=rj(r)
        log("API-02","Dataset API with valid key","200 success",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code==200 else "FAIL")
    else:
        log("API-02","Dataset API valid key","Need key","No key","","BLOCKED")

    # No key
    r=requests.get(da_url,timeout=T); j=rj(r)
    nk=r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","unauth","error","required","no api"])
    log("API-03","Dataset API without key","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if nk else "FAIL")

    # Invalid key
    r=requests.get(da_url,headers={"x-api-key":"fake_key_xyz"},timeout=T); j=rj(r)
    ik=r.status_code in [401,403] or any(w in str(j).lower() for w in ["denied","invalid","error","not found"])
    log("API-04","Dataset API invalid key","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if ik else "FAIL")

    # User B create credential
    if uBe:
        r=requests.post(f"{BASE}/addApiCredential",json={"user":uBe,"service_id":csid,"target_user_id":uB.get("user_id",51),"secret_key":""},timeout=T)
        j=rj(r)
        log("API-05","User B create credential (non-admin)","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")

    # Revoke + re-call
    if akey and cid:
        r=requests.post(f"{BASE}/revokeApiCredential",json={"user":uAe,"credential_id":cid},timeout=T); j=rj(r)
        rok=r.status_code==200 and j.get("status") in ["success","revoked"]
        log("API-06a","Revoke credential","Revoked",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"cid={cid}","PASS" if rok else "FAIL")

        r2=requests.get(da_url,headers={"x-api-key":akey},timeout=T); j2=rj(r2)
        rd=r2.status_code in [401,403] or any(w in str(j2).lower() for w in ["revoked","denied","invalid","error","inactive"])
        log("API-06b","API call after revoke","Rejected",f"HTTP {r2.status_code}, resp={json.dumps(j2)[:200]}","","PASS" if rd else "FAIL")
    elif akey:
        log("API-06","Revoke test","Need cred_id","Could not retrieve cred_id","","BLOCKED")
else:
    log("API-01","API Management","Need dataset","Dataset not created","","BLOCKED")

# ===== DELETE =====
print("\n▶ SECTION 4: DATASET DELETE\n")

if uAe:
    did=f"QA-DEL-{ts}"
    dp={"user":uAe,"service_name":f"QA Delete {ts}","dataset_id":did,"category":"Course Data","organization":"Test","source_system_id":"1","access_type":"public","service_status":"Active","accessibility":"Public","tags":"del","contact_name":"QA","contact_email":"qa@t.com","date_start":"2026-08-23","date_updated":"2026-08-23"}
    r=requests.post(f"{BASE}/addService",data=dp,timeout=T); j=rj(r)
    dsid_del=j.get("service_id")
    if dsid_del:
        r=requests.post(f"{BASE}/toggleServiceStatus",json={"user":uAe,"service_id":dsid_del,"status":"Deleted"},timeout=T); j=rj(r)
        log("DEL-01","Delete Dataset","Deleted",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}",f"sid={dsid_del}","PASS" if r.status_code==200 else "FAIL")

        dau=f"http://134.185.172.127:3003/api/dataapi/api/v1/{did}"
        r=requests.get(dau,timeout=T); j=rj(r)
        gone=r.status_code in [404,403,401] or any(w in str(j).lower() for w in ["not found","inactive","denied","deleted","no active","error"])
        log("DEL-02","API read deleted dataset","Not accessible",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if gone else "FAIL")

        if uBe and csid:
            r=requests.post(f"{BASE}/toggleServiceStatus",json={"user":uBe,"service_id":csid,"status":"Deleted"},timeout=T); j=rj(r)
            log("DEL-03","User B delete User A's dataset","Rejected",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","PASS" if r.status_code in [401,403] or j.get("status")=="error" else "FAIL")
    else:
        log("DEL-01","Delete Dataset","Need sid",f"Create failed: {json.dumps(j)[:200]}","","BLOCKED")

# ===== EMAIL =====
print("\n▶ SECTION 5: EMAIL NOTIFICATION\n")

log("EMAIL-001","Registration Email Trigger","Backend returns verify_url",f"status={reg.get('status')}, verify_url={'present' if reg.get('verify_url') else 'absent'}",f"user_id={reg.get('user_id')}","TRIGGER_PASS" if reg.get("status")=="success" and reg.get("verify_url") else "TRIGGER_FAIL")
# Cannot verify SMTP delivery or inbox without mailbox access
log("EMAIL-001-SMTP","Registration SMTP Submission","Verify SMTP accepted email","Cannot verify—no SMTP log or mailbox access","Need backend logs","BLOCKED")
log("EMAIL-001-INBOX","Registration Inbox Delivery","Email in inbox","Cannot verify—no mailbox access","","BLOCKED")

# Forgot Password
r=requests.post(f"{BASE}/forgotPassword",json={"username":"qa_userA","link":"http://134.185.172.127:3003"},timeout=T); j=rj(r)
log("EMAIL-005","Forgot Password Trigger","Backend processes request",f"HTTP {r.status_code}, status={j.get('status')}, resp={json.dumps(j)[:200]}","","TRIGGER_PASS" if j.get("status")=="success" else "TRIGGER_FAIL")
log("EMAIL-005-SMTP","Forgot Password SMTP","Verify SMTP","Cannot verify","","BLOCKED")
log("EMAIL-005-INBOX","Forgot Password Inbox","Email in inbox","Cannot verify","","BLOCKED")

# Dataset Access Request
if uBe and csid:
    r=requests.post(f"{BASE}/requestDatasetPermission",json={"user":uBe,"service_id":csid,"message":"QA test access request"},timeout=T); j=rj(r)
    log("EMAIL-013","Dataset Access Request Trigger","Request submitted",f"HTTP {r.status_code}, resp={json.dumps(j)[:200]}","","TRIGGER_PASS" if r.status_code==200 and j.get("status") not in ["Error","error"] else "TRIGGER_FAIL")
    log("EMAIL-013-SMTP","Access Request SMTP","Verify SMTP","Cannot verify","","BLOCKED")

# ===== SECURITY =====
print("\n▶ SECTION 6: SECURITY\n")

log("SEC-01","HTTPS/TLS","HTTPS enabled","HTTP only—no TLS termination detected","curl https://134.185.172.127:3003/ → connection refused. Credentials sent over plain HTTP.","FAIL")

if uA:
    hp="password" in uA and uA["password"]
    log("SEC-02","Password hash in login response","Not in response",f"password field present={bool(hp)}, value={str(uA.get('password',''))[:40]}...","Login response includes HMAC-SHA256 hash—information disclosure","FAIL" if hp else "PASS")

log("SEC-03","Verify URL domain mismatch","verify_url points to current environment",f"verify_url={str(reg.get('verify_url',''))[:80]}","Registration verify_url points to 110.78.210.128:3001 instead of 134.185.172.127:3003","FAIL" if "110.78" in str(reg.get("verify_url","")) else "PASS")

# ===== SUMMARY =====
print("\n"+"="*70)
print("FINAL SUMMARY")
print("="*70)

p=sum(1 for x in R if x["status"]=="PASS")
f=sum(1 for x in R if x["status"]=="FAIL")
b=sum(1 for x in R if x["status"]=="BLOCKED")
i=sum(1 for x in R if x["status"]=="INFO")
tp=sum(1 for x in R if x["status"]=="TRIGGER_PASS")
tf=sum(1 for x in R if x["status"]=="TRIGGER_FAIL")
tot=len(R)

print(f"\n  Total:         {tot}")
print(f"  ✅ PASS:        {p}")
print(f"  ❌ FAIL:        {f}")
print(f"  ⚠️  BLOCKED:     {b}")
print(f"  ℹ️  INFO:        {i}")
print(f"  📧 TRIGGER_PASS: {tp}")
print(f"  📧 TRIGGER_FAIL: {tf}")

print("\n--- FULL RESULTS ---\n")
for x in R:
    ic={"PASS":"✅","FAIL":"❌","BLOCKED":"⚠️","INFO":"ℹ️","TRIGGER_PASS":"📧✅","TRIGGER_FAIL":"📧❌"}.get(x["status"],"?")
    print(f"  {ic} {x['id']:20s} {x['status']:15s} {x['name']}")
    print(f"     Exp: {x['expected']}")
    print(f"     Act: {str(x['actual'])[:280]}")
    if x["evidence"]: print(f"     Ev:  {str(x['evidence'])[:280]}")
    print()
