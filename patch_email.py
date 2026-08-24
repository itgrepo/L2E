import re
with open('/Users/natthawutjantakul/intelligist_dataX/backendold/Astro_backend/app/ServiceConfig/email_service.py', 'r') as f:
    content = f.read()

new_content = content.replace('''        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            server.starttls()
            
        server.login(MAIL_USERNAME, MAIL_PASSWORD)''', '''        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
            if MAIL_USERNAME: server.login(MAIL_USERNAME, MAIL_PASSWORD)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USERNAME: 
                server.starttls()
                server.login(MAIL_USERNAME, MAIL_PASSWORD)''')

with open('/Users/natthawutjantakul/intelligist_dataX/backendold/Astro_backend/app/ServiceConfig/email_service.py', 'w') as f:
    f.write(new_content)
