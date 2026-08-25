import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import threading

MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'learn2earn@bde.go.th')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'L2E@Start2026!')
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'outgoing.workd.go.th')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() == 'true'
MAIL_FROM = os.environ.get('MAIL_FROM', "L2E Data Exchange <learn2earn@bde.go.th>").strip('"')
BASE_URL = os.environ.get('FRONTEND_URL', 'http://134.185.172.127:3003')

def _send_email_task(to_emails, subject, body_html):
    print(f"Sending email to {to_emails}", flush=True)
    if not to_emails:
        return
        
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
            if MAIL_USERNAME: server.login(MAIL_USERNAME, MAIL_PASSWORD)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USERNAME: 
                server.starttls()
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
        
        for email_addr in to_emails:
            if not email_addr: continue
            msg = MIMEMultipart()
            msg['From'] = MAIL_FROM
            msg['To'] = email_addr
            msg['Subject'] = subject
            msg.attach(MIMEText(body_html, 'html', "utf-8"))
            
            try:
                server.sendmail(MAIL_FROM, email_addr, msg.as_string())
            except Exception as e:
                print(f"Error sending email to {email_addr}: {e}")
                
        server.quit()
    except Exception as e:
        print(f"Failed to connect to SMTP server: {e}")

def send_email_async(to_emails, subject, body_html):
    # Make synchronous for uWSGI compatibility
    _send_email_task(to_emails, subject, body_html)

def notify_dataset_created(dataset_name, dataset_desc, to_emails):
    subject = f"New Dataset Available: {dataset_name}"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #19b5fe;">New Dataset Created</h2>
        <p>A new dataset has been published on DataX Portal.</p>
        <p><strong>Name:</strong> {dataset_name}</p>
        <p><strong>Description:</strong> {dataset_desc}</p>
        <br>
        <a href="{BASE_URL}/catalog" style="display: inline-block; padding: 10px 20px; background-color: #19b5fe; color: white; text-decoration: none; border-radius: 4px;">View Catalog</a>
    </div>
    """
    send_email_async(to_emails, subject, body)

def notify_dataset_updated(dataset_name, to_emails):
    subject = f"Dataset Updated: {dataset_name}"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #f59e0b;">Dataset Updated</h2>
        <p>The dataset <strong>{dataset_name}</strong> has been modified.</p>
        <br>
        <a href="{BASE_URL}/catalog" style="display: inline-block; padding: 10px 20px; background-color: #f59e0b; color: white; text-decoration: none; border-radius: 4px;">View Dataset</a>
    </div>
    """
    send_email_async(to_emails, subject, body)

def notify_access_request(dataset_name, requester_name, to_emails):
    subject = f"New Access Request for {dataset_name}"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #19b5fe;">Access Request</h2>
        <p>User <strong>{requester_name}</strong> has requested access to the dataset <strong>{dataset_name}</strong>.</p>
        <p>Please log in to the admin panel to review and approve/reject this request.</p>
        <br>
        <a href="{BASE_URL}/dataset-approval" style="display: inline-block; padding: 10px 20px; background-color: #19b5fe; color: white; text-decoration: none; border-radius: 4px;">Manage Requests</a>
    </div>
    """
    send_email_async(to_emails, subject, body)

def notify_access_approved(dataset_name, to_emails):
    subject = f"Access Granted: {dataset_name}"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #10b981;">Access Granted</h2>
        <p>Your request to access the dataset <strong>{dataset_name}</strong> has been approved by an administrator.</p>
        <p>You can now view and utilize this dataset.</p>
        <br>
        <a href="{BASE_URL}/catalog" style="display: inline-block; padding: 10px 20px; background-color: #10b981; color: white; text-decoration: none; border-radius: 4px;">View Dataset</a>
    </div>
    """
    send_email_async(to_emails, subject, body)

def notify_added_to_group(group_name, to_emails):
    subject = f"Added to Group: {group_name}"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #19b5fe;">Group Assignment</h2>
        <p>You have been assigned to the user group: <strong>{group_name}</strong>.</p>
        <p>This may grant you access to new datasets and features associated with this group.</p>
    </div>
    """
    send_email_async(to_emails, subject, body)
def notify_verification_email(firstname, lastname, verify_url, to_emails):
    subject = "Verify Email Address for DataX Portal"
    body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2 style="color: #19b5fe;">Verify Your Email Address</h2>
        <p>Hi {firstname} {lastname},</p>
        <p>Thank you for signing up with DataX Portal.</p>
        <p>Please click the button below to verify your email address and activate your account:</p>
        <br>
        <a href="{verify_url}" style="display: inline-block; padding: 12px 24px; background-color: #19b5fe; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Verify Email</a>
        <br><br>
        <p style="font-size: 12px; color: #777;">If you did not register for an account, please ignore this email.</p>
    </div>
    """
    send_email_async(to_emails, subject, body)
