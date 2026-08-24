import requests
import json
import base64
from urllib.parse import quote

password = "password123"
# mimic frontend encodePassword
enc = '$e$' + base64.b64encode(quote(password).encode()).decode('utf-8')[::-1]

payload = {
    "username": "testadmin",
    "password": enc,
    "link": "http://134.185.172.127:3003"
}
headers = {'Content-Type': 'application/json'}

try:
    r = requests.post('http://134.185.172.127:3003/api/login', json=payload)
    print("Status:", r.status_code)
    print("Response:", r.text)
except Exception as e:
    print(e)
