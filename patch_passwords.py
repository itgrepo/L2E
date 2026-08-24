import os
import re

# We will search and replace in files
backend_path = "/home/ubuntu/Intelligist_DataX_Deploy_3003/backendold/Astro_backend/app/"
files_to_patch = [
    "ServiceConfig/login.py",
    "ServiceConfig/register.py",
    "Management/rolesMgmt.py"
]

def patch_file(filepath, replacements):
    with open(filepath, "r") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, "w") as f:
        f.write(content)

# login.py replacements
login_replacements = [
    # In login()
    ("password = dataInput['password']", "password = hash_password(dataInput['password'])"),
    # In resetPasswordByToken()
    ("new_password = dataInput.get('password')", "new_password = hash_password(dataInput.get('password'))"),
    # In resetPassword() (if they use it)
    ("password = dataInput['password']", "password = hash_password(dataInput['password'])"),
    ("currentPassword = dataInput['currentPassword']", "currentPassword = hash_password(dataInput['currentPassword'])")
]

# register.py replacements
register_replacements = [
    # In registerSimple()
    ("password = dataInput['password']", "password = hash_password(dataInput['password'])")
]

# rolesMgmt.py replacements
roles_replacements = [
    # In createUser()
    ("password = dataInput.get('password')", "password = hash_password(dataInput.get('password'))")
]

patch_file(os.path.join(backend_path, files_to_patch[0]), login_replacements)
patch_file(os.path.join(backend_path, files_to_patch[1]), register_replacements)
patch_file(os.path.join(backend_path, files_to_patch[2]), roles_replacements)
print("Files patched.")
