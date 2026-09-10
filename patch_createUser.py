import codecs
import re

with codecs.open('backendold/Astro_backend/app/Management/rolesMgmt.py', 'r', 'utf-8') as f:
    content = f.read()

# We need to inject the email import at the top of the file if not present
if 'notify_verification_email' not in content:
    content = content.replace('from ServiceConfig import *', 'from ServiceConfig import *\nfrom app.ServiceConfig.email_service import notify_verification_email')

# Find the place where user_id is retrieved
target = "user_id = cursor.lastrowid"
injection = """user_id = cursor.lastrowid
        
        # If pending verification (4), generate token and send email
        if int(status_id) == 4:
            import uuid
            token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
            sql_token = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
            cursor.execute(sql_token, (token, username, email, 'active'))
            
            try:
                # Use same LINK logic as registerSimple
                # We can assume request.host_url or a fallback
                fallback_link = "http://learn2earndatax.bde.go.th"
                link = dataInput.get('link', fallback_link)
                verify_url = f"{link}/verify/{token}"
                notify_verification_email(username, '', verify_url, email)
                print(f"DEBUG: Admin AddUser Verification Email sent. URL: {verify_url}")
            except Exception as mail_err:
                print("Could not send verification email in Admin AddUser: " + str(mail_err))
"""
content = content.replace(target, injection)

with codecs.open('backendold/Astro_backend/app/Management/rolesMgmt.py', 'w', 'utf-8') as f:
    f.write(content)
