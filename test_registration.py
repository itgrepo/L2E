import requests, json, base64, time, re
import urllib.parse

BASE = 'http://localhost:3003/api'
MAILHOG = 'http://localhost:8028/api/v2/messages'
def ep(pw): return f'$e$={base64.b64encode(urllib.parse.quote(pw).encode()).decode()[::-1]}'

email = 'afourdy2134@gmail.com'
username = 'afourdy2134_test'

def clear_emails():
    try: requests.delete('http://localhost:8028/api/v1/messages', timeout=5)
    except: pass

def get_latest_email(subject_keyword):
    emails = requests.get(MAILHOG, timeout=5).json().get('items', [])
    for em in emails:
        subj = em.get('Content', {}).get('Headers', {}).get('Subject', [''])[0]
        if subject_keyword.lower() in subj.lower():
            body = em.get('Content', {}).get('Body', '')
            try:
                body = base64.b64decode(em['MIME']['Parts'][0]['Body']).decode('utf-8')
            except: pass
            return {'body': body, 'em': em}
    return None

def extract_link(body, keyword):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)
    for u in urls:
        if keyword in u: return u
    return None

clear_emails()

print("1. Registering...")
payload = {
    'username': username,
    'password': ep('Password@123'),
    'email': email,
    'firstname': 'test',
    'lastname': 'test',
    'organization': 'Intelligist',
    'link': 'http://134.185.172.127:3003'
}
r_reg = requests.post(f'{BASE}/registerSimple', json=payload)
print(f'Registration status: {r_reg.status_code}, body: {r_reg.text}')

time.sleep(3)
em_data = get_latest_email('Verify Email')
if not em_data:
    print("Verification email not found!")
    exit(1)

body = em_data['body']
link = extract_link(body, 'verify')
print(f"2. Found verification link: {link}")

token = link.split('token=')[1].split('&')[0] if 'token=' in link else link.split('/')[-1]

print("3. Verifying token...")
r_verify = requests.post(f'{BASE}/getEmailFromToken', json={'token': token})
print(f'Verify status: {r_verify.status_code}, body: {r_verify.text}')

print("4. First Login...")
r_login = requests.post(f'{BASE}/login', json={'username': username, 'password': ep('Password@123'), 'link': 'http://134.185.172.127:3003'})
print(f'Login status: {r_login.status_code}, body: {r_login.text}')

print("5. Triggering Password Change/Forgot Password Flow...")
clear_emails()
r_forgot = requests.post(f'{BASE}/forgotPassword', json={'username': username, 'link': 'http://134.185.172.127:3003'})
print(f'Forgot password request: {r_forgot.text}')

time.sleep(3)
em_reset = get_latest_email('Reset Password')
if not em_reset:
    print("Reset email not found!")
    exit(1)

body_reset = em_reset['body']
link_reset = extract_link(body_reset, 'resetpassword')
print(f"6. Found reset link: {link_reset}")
token_reset = link_reset.split('resetpassword/')[1]

print("7. Setting new password...")
r_reset = requests.post(f'{BASE}/resetPasswordByToken', json={'token': token_reset, 'password': ep('NewPassword@123')})
print(f'Reset submit status: {r_reset.status_code}, body: {r_reset.text}')

print("8. Login with NEW password...")
r_login_new = requests.post(f'{BASE}/login', json={'username': username, 'password': ep('NewPassword@123'), 'link': 'http://134.185.172.127:3003'})
print(f'Login (New PW) status: {r_login_new.status_code}, body: {r_login_new.text}')
