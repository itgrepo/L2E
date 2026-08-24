import re

with open('backendold/Astro_backend/app/ServiceConfig/register.py', 'r') as f:
    content = f.read()

# Add import if not exists
if 'from .email_service import' not in content:
    content = content.replace('from .groupMgmt import *', 'from .groupMgmt import *\nfrom .email_service import notify_verification_email')

# Replace the email sending logic
old_logic = '''            # Construct the verification link
            # Use provided link or fallback to global LINK
            base_link = link if link else LINK
            sendMailConfirmRegister(user_id, token, email, base_link, firstname, lastname)
            verify_url = f"{base_link}/verify/{token}"
            print(f"DEBUG: Verification Email simulated/sent. URL: {verify_url}")'''

new_logic = '''            base_link = link if link else LINK
            verify_url = f"{base_link}/verify/{token}"
            notify_verification_email(firstname, lastname, verify_url, email)
            print(f"DEBUG: Verification Email simulated/sent. URL: {verify_url}")'''

content = content.replace(old_logic, new_logic)

with open('backendold/Astro_backend/app/ServiceConfig/register.py', 'w') as f:
    f.write(content)
