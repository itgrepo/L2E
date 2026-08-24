import requests, json, base64, time
from urllib.parse import quote
BASE = 'http://localhost:3003/api'
MAILHOG = 'http://localhost:8028/api/v2/messages'
def ep(pw): return f'$e$={base64.b64encode(quote(pw).encode()).decode()[::-1]}'
def pe(d): return base64.b64encode(json.dumps(d).encode()).decode()[::-1]+'==e=='
print('Logging in admin...')
r = requests.post(f'{BASE}/login', json={'username':'qa_admin2','password':ep('Password@123'),'link':'http://134.185.172.127:3003'}, timeout=5)
admin_user = r.json().get('data')
admin_user_encoded = pe(admin_user)
admin_id = admin_user['user_id']
print(f'Admin: {admin_id}')

def get_emails():
    try: return requests.get(MAILHOG, timeout=5).json().get('items', [])
    except Exception as e: 
        print(f"Error fetching mailhog: {e}")
        return []

print('Clearing emails...')
try: requests.delete('http://localhost:8028/api/v1/messages', timeout=5)
except: pass

def test_dataset(access_type):
    print(f'\n--- Testing {access_type} Dataset ---')
    ds_name = f'QA-E2E-{access_type}-{int(time.time())}'
    payload = {
        'user': admin_user_encoded,
        'service_name': ds_name, 'dataset_id': ds_name, 'source_system_id': '1', 'category': '', 'organization': '',
        'description': 'QA E2E Test',
        'access_type': access_type,
        'accessibility': access_type,
        'data_source': 'database',
        'service_status': 'Active'
    }
    r = requests.post(f'{BASE}/addService', data=payload, timeout=5)
    print(f'Create DS: {r.status_code}')
    
    # Check email
    time.sleep(2)
    emails = get_emails()
    found = False
    for em in emails:
        subj = em.get('Content', {}).get('Headers', {}).get('Subject', [''])[0]
        if 'New Dataset Available' in subj: found = True
    print(f'Email Triggered: {found}'); print('Subjects: ', [em.get('Content', {}).get('Headers', {}).get('Subject', [''])[0] for em in emails])
    try: requests.delete('http://localhost:8028/api/v1/messages', timeout=5)
    except: pass

    # Get service ID
    r = requests.post(f'{BASE}/getService', json={'user': admin_user_encoded}, timeout=5)
    my_ds = next((s for s in r.json().get('data', []) if s['service_name'] == ds_name), None)
    sid = my_ds['service_id']
    dataset_id = my_ds['dataset_id']
    print(f'Service ID: {sid}, Dataset ID: {dataset_id}')
    
    # API-1
    print('Testing API Type 1 (Public)')
    cfg = {'user': admin_user_encoded, 'service_id': sid, 'api_enabled': 'true', 'api_type': 'public', 'api_db_name': 'datax_db_3003', 'api_source_type': 'table', 'api_source_name': 'api_management_test_data', 'api_request_fields': ['province'], 'api_response_fields': ['id', 'province', 'status', 'display_name']}
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    r = requests.get(f'{BASE.replace("/api", "/dataapi")}/api/v1/{dataset_id}', timeout=5)
    print(f'API-1 (No Key) Status: {r.status_code}, Rows: {len(r.json()) if isinstance(r.json(), list) else r.text[:50]}')

    # API-2
    print('Testing API Type 2 (Private)')
    cfg['api_type'] = 'private'
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    r = requests.get(f'{BASE.replace("/api", "/dataapi")}/api/v1/{dataset_id}', timeout=5)
    print(f'API-2 (No Key) Reject Status: {r.status_code}')
    
    r = requests.post(f'{BASE}/addApiCredential', json={'user': admin_user_encoded, 'service_id': sid, 'api_type': 'private', 'target_user_id': admin_id}, timeout=5)
    key = r.json().get('secret_key')
    print(f'API-2 Credential Created: {bool(key)}')
    if key:
        r = requests.get(f'{BASE.replace("/api", "/dataapi")}/api/v1/{dataset_id}', headers={'x-api-key': key}, timeout=5)
        print(f'API-2 (Valid Key) Status: {r.status_code}, Rows: {len(r.json()) if isinstance(r.json(), list) else r.text[:50]}')
        
    # API-3
    print('Testing API Type 3 (Scope)')
    cfg['api_type'] = 'scope'
    requests.post(f'{BASE}/saveApiConfig', json=cfg, timeout=5)
    if key:
        scope = [{'field': 'province', 'operator': '=', 'value': 'Bangkok', 'logic': 'AND'}]
        requests.post(f'{BASE}/saveApiScopeForUser', json={'user': admin_user_encoded, 'service_id': sid, 'target_user_id': admin_id, 'scope_json': json.dumps(scope)}, timeout=5)
        r = requests.get(f'{BASE.replace("/api", "/dataapi")}/api/v1/{dataset_id}', headers={'x-api-key': key}, timeout=5)
        data = r.json()
        if isinstance(data, list):
            print(f'API-3 (Valid Key) Status: {r.status_code}, Rows: {len(data)}, All BKK: {all(d.get("province") == "Bangkok" for d in data)}')
        else:
            print(f'API-3 (Valid Key) Status: {r.status_code}, Resp: {str(r.text)[:50]}')

test_dataset('public')
test_dataset('restricted')
print('Done!')
