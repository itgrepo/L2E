import requests, json, base64, time
from urllib.parse import quote

BASE = 'http://localhost:3003/api'
MAILHOG = 'http://localhost:8028/api/v2/messages'
def ep(pw): return f'$e$={base64.b64encode(quote(pw).encode()).decode()[::-1]}'
def pe(d): return base64.b64encode(json.dumps(d).encode()).decode()[::-1]+'==e=='

# Logins
r_admin = requests.post(f'{BASE}/login', json={'username':'qa_admin2','password':ep('Password@123'),'link':'http://134.185.172.127:3003'}, timeout=5)
admin_user_encoded = pe(r_admin.json().get('data'))
admin_id = r_admin.json().get('data')['user_id']

r_user = requests.post(f'{BASE}/login', json={'username':'qa_user2','password':ep('Password@123'),'link':'http://134.185.172.127:3003'}, timeout=5)
normal_user_encoded = pe(r_user.json().get('data'))
normal_id = r_user.json().get('data')['user_id']

def get_emails():
    try: return requests.get(MAILHOG, timeout=5).json().get('items', [])
    except Exception as e: return []
def clear_emails():
    try: requests.delete('http://localhost:8028/api/v1/messages', timeout=5)
    except: pass

def test_dataset(access_type):
    print(f'\n========== Testing Dataset Type: {access_type} ==========')
    ds_name = f'QA-E2E-{access_type}-{int(time.time())}'
    clear_emails()
    
    # 1. Create Dataset
    payload = {
        'user': admin_user_encoded,
        'service_name': ds_name,
        'description': f'Test {access_type}',
        'access_type': access_type,
        'dataset_id': ds_name,
        'source_system_id': '1',
        'category': '',
        'organization': '',
        'accessibility': access_type.capitalize(),
        'data_source': 'database',
        'service_status': 'Active'
    }
    r_create = requests.post(f'{BASE}/addService', data=payload, timeout=5)
    print(f'[Dataset Create] {r_create.status_code}')
    
    # Wait for Dataset Creation Email
    time.sleep(3)
    emails = get_emails()
    ds_email_found = any('New Dataset Available' in em.get('Content', {}).get('Headers', {}).get('Subject', [''])[0] for em in emails)
    actual_recipients = []
    has_pii_leak = False
    for em in emails:
        to_headers = em.get('Content', {}).get('Headers', {}).get('To', [])
        actual_recipients.extend(to_headers)
        body = em.get('Content', {}).get('Body', '')
        if access_type == 'pii' and ('phone' in body.lower() or 'email' in body.lower() or 'card' in body.lower()): # naive check
            has_pii_leak = True
            
    print(f'[Email - Dataset Created] Triggered: {ds_email_found}, Actual Recipients: {len(actual_recipients)}')
    if access_type == 'pii': print(f'[Email - PII Security] Has Leak: {has_pii_leak}')
    clear_emails()

    # Get service ID
    r_get = requests.post(f'{BASE}/getService', json={'user': admin_user_encoded}, timeout=5)
    my_ds = next((s for s in r_get.json().get('data', []) if s['service_name'] == ds_name), None)
    sid = my_ds['service_id']
    dataset_id = my_ds['dataset_id']
    
    # helper for api access
    def call_api(key=None):
        headers = {'x-api-key': key} if key else {}
        return requests.get(f'{BASE.replace("/api", "/dataapi")}/api/v1/{dataset_id}', headers=headers, timeout=5)
    
    # Create Wrong Dataset Credential (for auth testing)
    r_wrong = requests.post(f'{BASE}/addApiCredential', json={'user': admin_user_encoded, 'service_id': 99999, 'api_type': 'private', 'target_user_id': admin_id}, timeout=5)
    wrong_key = r_wrong.json().get('secret_key') if r_wrong.status_code == 200 else 'wrong-key-fallback'

    # --- API 1: Public ---
    print('\n--- API Type: Public ---')
    cfg = {'user': admin_user_encoded, 'service_id': sid, 'api_enabled': 'true', 'api_type': 'public', 'api_db_name': 'datax_db_3003', 'api_source_type': 'table', 'api_source_name': 'api_management_test_data', 'api_request_fields': ['province'], 'api_response_fields': ['id', 'province', 'status', 'display_name']}
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    
    time.sleep(2)
    pub_emails = get_emails()
    pub_email_found = len(pub_emails) > 0
    print(f'[Email - Public API Created] Triggered: {pub_email_found}')
    clear_emails()
    
    r_pub = call_api()
    print(f'[Public API] No Key Status: {r_pub.status_code}')

    # --- API 2: Private ---
    print('\n--- API Type: Private ---')
    cfg['api_type'] = 'private'
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    
    time.sleep(2)
    priv_emails = get_emails()
    priv_email_found = len(priv_emails) > 0
    print(f'[Email - Private API Created] Triggered: {priv_email_found}')
    clear_emails()
    
    r_priv_cred = requests.post(f'{BASE}/addApiCredential', json={'user': admin_user_encoded, 'service_id': sid, 'api_type': 'private', 'target_user_id': admin_id}, timeout=5)
    valid_key = r_priv_cred.json().get('secret_key')
    
    print(f'[Private API] No Key: {call_api().status_code}')
    print(f'[Private API] Invalid Key: {call_api("INVALID_KEY").status_code}')
    print(f'[Private API] Wrong Dataset Key: {call_api(wrong_key).status_code}')
    print(f'[Private API] Valid Key: {call_api(valid_key).status_code}')

    # --- API 3: Scope ---
    print('\n--- API Type: Scope ---')
    cfg['api_type'] = 'scope'
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    
    time.sleep(2)
    scope_emails = get_emails()
    scope_email_found = len(scope_emails) > 0
    print(f'[Email - Scope API Created] Triggered: {scope_email_found}')
    clear_emails()
    
    scope = [{'field': 'province', 'operator': '=', 'value': 'Bangkok', 'logic': 'AND'}]
    requests.post(f'{BASE}/saveApiScopeForUser', json={'user': admin_user_encoded, 'service_id': sid, 'target_user_id': admin_id, 'scope_json': json.dumps(scope)}, timeout=5)
    
    print(f'[Scope API] No Key: {call_api().status_code}')
    r_scope_valid = call_api(valid_key)
    print(f'[Scope API] Valid Key Status: {r_scope_valid.status_code}')

test_dataset('public')
test_dataset('internal')
test_dataset('restricted')
test_dataset('pii')
