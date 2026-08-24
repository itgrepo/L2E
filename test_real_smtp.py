import requests, json, base64, time
import urllib.parse
import subprocess

BASE = 'http://localhost:3003/api'
def ep(pw): return f'$e$={base64.b64encode(urllib.parse.quote(pw).encode()).decode()[::-1]}'

email = 'afourdy2134@gmail.com'
username = 'qa_mailflow_' + str(int(time.time()))
password_old = 'QaTest@123!'
password_new = 'QaTest@456!'

print(f"--- STARTING REAL SMTP TEST FOR {username} ---")

print("\n1. Registering...")
payload = {
    'username': username,
    'password': ep(password_old),
    'email': email,
    'firstname': 'QA',
    'lastname': 'Engineer',
    'organization': 'QA Dept',
    'link': 'http://134.185.172.127:3003'
}
r_reg = requests.post(f'{BASE}/registerSimple', json=payload)
print(f'Registration status: {r_reg.status_code}, body: {r_reg.text}')
if r_reg.status_code != 200:
    print("Registration Failed!")
    exit(1)

res_json = r_reg.json()
token = res_json.get('token')
print(f"Extracted Verification Token from API: {token}")

time.sleep(3)
print("\n3. Verifying token...")
r_verify = requests.post(f'{BASE}/getEmailFromToken', json={'token': token})
print(f'Verify status: {r_verify.status_code}, body: {r_verify.text}')

print("\n4. First Login...")
r_login = requests.post(f'{BASE}/login', json={'username': username, 'password': ep(password_old), 'link': 'http://134.185.172.127:3003'})
print(f'Login status: {r_login.status_code}, body: {r_login.text}')

print("\n5. Triggering Password Change/Forgot Password Flow...")
r_forgot = requests.post(f'{BASE}/forgotPassword', json={'username': username, 'link': 'http://134.185.172.127:3003'})
print(f'Forgot password request: {r_forgot.text}')

time.sleep(3)
print("\n6. Fetching Reset Token from DB...")
cmd = f'sudo docker exec aee3755419dc_datax_db_3003 mysql -u astro -ppassword123 -s -N -e "USE datax_db_3003; SELECT token FROM token_forgotpassword WHERE email = \'{email}\' AND status = \'active\' ORDER BY created_at DESC LIMIT 1;"'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
token_reset = result.stdout.strip()
print(f"Extracted Reset Token from DB: {token_reset}")

print("\n7. Setting new password...")
r_reset = requests.post(f'{BASE}/resetPasswordByToken', json={'token': token_reset, 'password': ep(password_new)})
print(f'Reset submit status: {r_reset.status_code}, body: {r_reset.text}')

print("\n8. Password Verification...")
print("  a. Login with OLD password...")
r_login_old = requests.post(f'{BASE}/login', json={'username': username, 'password': ep(password_old), 'link': 'http://134.185.172.127:3003'})
print(f'  Login (Old PW) status: {r_login_old.status_code}, body: {r_login_old.text}')

print("  b. Login with NEW password...")
r_login_new = requests.post(f'{BASE}/login', json={'username': username, 'password': ep(password_new), 'link': 'http://134.185.172.127:3003'})
print(f'  Login (New PW) status: {r_login_new.status_code}, body: {r_login_new.text}')
