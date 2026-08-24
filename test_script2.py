import requests, json, base64
from urllib.parse import quote
BASE = 'http://localhost:3003/api'
def ep(pw): return f'$e$={base64.b64encode(quote(pw).encode()).decode()[::-1]}'
def pe(d): return base64.b64encode(json.dumps(d).encode()).decode()[::-1]+'==e=='
r = requests.post(f'{BASE}/login', json={'username':'qa_admin2','password':ep('Password@123'),'link':'http://134.185.172.127:3003'}, timeout=5)
admin_user_encoded = pe(r.json().get('data'))
r = requests.post(f'{BASE}/getService', json={'user': admin_user_encoded}, timeout=5)
print(r.status_code)
print(r.text[:500])
