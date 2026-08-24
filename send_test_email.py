import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

fromaddr = "L2E Data Exchange <learn2earn@bde.go.th>"
toaddr = "learn2earn@bde.go.th"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Verify Email Address for L2E Data Exchange"

link = "http://134.185.172.127:3003/verify-email?token=test_token_123456"
firstname = "Nutthawut"
lastname = "Ja"

body = f"""<p style='font-size: 14px;width: 550px;'>Hi&nbsp;&nbsp;{firstname}&nbsp;{lastname}<br>Thank you for signing up with L2E Data Exchange.<br> Please click the \"Verify Email\" button below to verify your email address.</p> <a href='{link}' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Verify Email</a>"""

msg.attach(MIMEText(body, 'html', "utf-8"))

try:
    server = smtplib.SMTP_SSL('outgoing.workd.go.th', 465)
    server.set_debuglevel(1)
    server.login('learn2earn@bde.go.th', 'L2E@Start2026!')
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print("EMAIL SENT SUCCESSFULLY")
except Exception as e:
    print("ERROR:", e)
