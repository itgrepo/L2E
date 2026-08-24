import smtplib
from email.mime.text import MIMEText
try:
    msg = MIMEText('Test email with timeout=5.')
    msg['Subject'] = 'Test Email Timeout'
    msg['From'] = 'learn2earn@bde.go.th'
    msg['To'] = 'auto.athiprat@gmail.com'
    server = smtplib.SMTP_SSL('outgoing.workd.go.th', 465, timeout=5)
    server.login('learn2earn@bde.go.th', 'L2E@Start2026!')
    server.sendmail('learn2earn@bde.go.th', 'auto.athiprat@gmail.com', msg.as_string())
    print('SUCCESS')
    server.quit()
except Exception as e:
    print('ERROR:', e)
