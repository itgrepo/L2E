import urllib.request
import json
import base64
import random
import string
import urllib.parse

def encode_user_data(user_data):
    json_str = json.dumps(user_data)
    # Equivalent to JS: btoa(unescape(encodeURIComponent(json_str)))
    encoded = urllib.parse.quote(json_str)
    # JS unescape just decodes %XX to chars. In Python we can just encode to utf-8.
    b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    reversed_b64 = b64[::-1]
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return reversed_b64 + random_chars

payload = {
    "user": encode_user_data({"username": "admin", "org_id": "1", "previlage_id": "3"}),
    "db_name": "STG_DATAEXCHAGE",
    "table_name": "STG_THAIMOOC_API_RAW"
}

req = urllib.request.Request(
    'http://dexuat.duckdns.org:3003/api/previewTableData',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:")
    print(response.read().decode('utf-8'))
except urllib.error.URLError as e:
    print("ERROR:")
    print(e.read().decode('utf-8'))
