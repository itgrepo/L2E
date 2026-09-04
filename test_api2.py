import requests
import json

url = "http://134.185.172.127:3003/getTableColumns"
headers = {"Content-Type": "application/json"}
payload = {
    "db_name": "STG_DATAEXCHAGE",
    "table_name": "STG_EWE_COURSE"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
