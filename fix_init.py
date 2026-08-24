import os
import re

init_path = "/home/ubuntu/Intelligist_DataX_Deploy_3003/backendold/Astro_backend/app/ServiceConfig/__init__.py"

with open(init_path, "r") as f:
    content = f.read()

new_hash_func = """import base64
from urllib.parse import unquote

def decode_frontend_password(pwd):
    if not pwd or not isinstance(pwd, str):
        return pwd
    if pwd.startswith('$e$'):
        try:
            b64 = pwd[3:][::-1]
            return unquote(base64.b64decode(b64).decode('utf-8'))
        except Exception as e:
            return pwd
    return pwd

def hash_password(password):
    if not password:
        return password
    password = str(password)
    
    # Check if already SHA-256 hex string
    if len(password) == 64 and all(c in "0123456789abcdefABCDEF" for c in password):
        return password
        
    password = decode_frontend_password(password)
    
    key = b"e9NHdT3GU6wBdWlw3RTqvrShGzyerRl4BaMhFeUI3v4j6U0opW5a19HQHDAHHCrhYXq8oG6D"
    msg = password.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()"""

content = re.sub(r"def decode_frontend_password\(pwd\):.*?(?=\n\n|\Z)", "", content, flags=re.DOTALL)
content = re.sub(r"def hash_password\(password\):.*?(?=\n\n|\Z)", new_hash_func, content, flags=re.DOTALL)

with open(init_path, "w") as f:
    f.write(content)
