import urllib.request
import json

url = "http://localhost:3015/getEmailFromToken"
data = {
    "token": "17c3cb5e92624f98b1ef1645661356b8247a30e8a61311f1ac2cc2cf710c7508"
}
req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
