import urllib.request
import json

url = "http://localhost:3015/registerSimple"
data = {
    "username": "learn2earn",
    "email": "learn2earn@bde.go.th",
    "password": "$e$=Qmcwc3czBEU",
    "firstname": "Learn",
    "lastname": "ToEarn",
    "organization": "1"
}
req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
