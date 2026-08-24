import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pymysql
import re
from datetime import datetime, timedelta

def get_valid_emails():
    try:
        conn = pymysql.connect(
            host="db",
            user="astro",
            password="password123",
            database="datax_db_3003",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user WHERE email IS NOT NULL AND status_account = "active";')
        emails = [row[0] for row in cursor.fetchall() if row[0]]
        cursor.close()
        conn.close()
        
        valid_emails = []
        regex = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
        for email in emails:
            if re.match(regex, email):
                valid_emails.append(email)
        return list(set(valid_emails))
    except Exception as e:
        print(f"DB Error: {e}")
        return ["afourdy2134@gmail.com"]

def send_email(subject, html_content, to_emails):
    if not to_emails:
        return
    print(f"Sending '{subject}' to {len(to_emails)} recipients...")
    try:
        server = smtplib.SMTP_SSL("outgoing.workd.go.th", 465)
        server.login("learn2earn@bde.go.th", "L2E@Start2026!")
        
        for email in to_emails:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = "L2E Data Exchange <learn2earn@bde.go.th>"
            msg["To"] = email
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            try:
                server.sendmail("L2E Data Exchange <learn2earn@bde.go.th>", email, msg.as_string())
                print(f"  -> Sent to {email}")
            except Exception as e:
                print(f"  -> Failed to send to {email}: {e}")
                
        server.quit()
    except Exception as e:
        print(f"SMTP Connect Error: {e}")

valid_emails = get_valid_emails()
print(f"Found {len(valid_emails)} valid emails.")

# 1. New Dataset
html1 = """
<div style="font-family: sans-serif; padding: 20px;">
    <h2 style="color: #2563eb;">New Dataset Available!</h2>
    <p>A new dataset has just been published on the DataX Portal.</p>
    <ul>
        <li><strong>Dataset Name:</strong> Public Demographics 2026</li>
        <li><strong>Publisher:</strong> Ministry of Data</li>
        <li><strong>Access Type:</strong> Public</li>
    </ul>
    <p>You can browse and request access to this dataset on the portal.</p>
</div>
"""
send_email("Notification: New Dataset Added to DataX", html1, valid_emails)

# 2. New API Added
now = datetime.now()
expire = now + timedelta(days=365)
html2 = f"""
<div style="font-family: sans-serif; padding: 20px;">
    <h2 style="color: #16a34a;">New API Endpoint Ready</h2>
    <p>A new API has been configured and is now available for integration.</p>
    <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td bgcolor="#f3f4f6"><strong>API Name</strong></td><td>Demographics V2 API</td></tr>
        <tr><td bgcolor="#f3f4f6"><strong>Creation Date</strong></td><td>{now.strftime("%Y-%m-%d")}</td></tr>
        <tr><td bgcolor="#f3f4f6"><strong>Creation Time</strong></td><td>{now.strftime("%H:%M:%S")}</td></tr>
        <tr><td bgcolor="#f3f4f6"><strong>Valid Until (Expiry)</strong></td><td>{expire.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
    </table>
    <p>Please secure your API keys.</p>
</div>
"""
send_email("Notification: New API Endpoint Configured", html2, valid_emails)

# 3. API Usage Alert
html3 = f"""
<div style="font-family: sans-serif; padding: 20px;">
    <h2 style="color: #dc2626;">API Usage Alert</h2>
    <p>We detected recent activity on your API endpoints.</p>
    <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td bgcolor="#fcfaca"><strong>User / Application</strong></td><td>Internal Analytics Bot</td></tr>
        <tr><td bgcolor="#fcfaca"><strong>Endpoint Accessed</strong></td><td>/api/v2/demographics (Public Route)</td></tr>
        <tr><td bgcolor="#fcfaca"><strong>Access Date</strong></td><td>{now.strftime("%Y-%m-%d")}</td></tr>
        <tr><td bgcolor="#fcfaca"><strong>Access Time</strong></td><td>{now.strftime("%H:%M:%S")}</td></tr>
        <tr><td bgcolor="#fcfaca"><strong>Status</strong></td><td>200 OK</td></tr>
    </table>
</div>
"""
send_email("Security Alert: API Endpoint Accessed", html3, valid_emails)

print("Simulation complete.")
