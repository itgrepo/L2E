filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/register.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """        # Try to send verification email (silently fail if SMTP not available)
        try:
            base_link = link if link else LINK
            verify_url = f"{base_link}/verify/{token}"
            notify_verification_email(firstname, lastname, verify_url, email)
            print(f"DEBUG: Verification Email simulated/sent. URL: {verify_url}")
        except Exception as mail_err:
            current_app.logger.warning("Could not send verification email: " + str(mail_err))
            verify_url = f"{LINK}/verify/{token}"

        logAction(user_id, '/registerSimple', 'User registered, pending email verification', 'info')

        return jsonify({
            'status': 'success',
            'message': 'สมัครสมาชิกสำเร็จ กรุณาตรวจสอบอีเมลเพื่อยืนยันตัวตน',
            'token': token,
            'user_id': user_id,
            'verify_url': verify_url # Return URL for Simulation UI
        })"""

new_code = """        # Try to send verification email (silently fail if SMTP not available)
        email_sent = True
        try:
            base_link = link if link else LINK
            verify_url = f"{base_link}/verify/{token}"
            notify_verification_email(firstname, lastname, verify_url, email)
            print(f"DEBUG: Verification Email simulated/sent. URL: {verify_url}")
        except Exception as mail_err:
            current_app.logger.warning("Could not send verification email: " + str(mail_err))
            verify_url = f"{LINK}/verify/{token}"
            email_sent = False

        logAction(user_id, '/registerSimple', 'User registered, pending email verification', 'info')

        return jsonify({
            'status': 'success',
            'message': 'สมัครสมาชิกสำเร็จ กรุณาตรวจสอบอีเมลเพื่อยืนยันตัวตน',
            'token': token,
            'user_id': user_id,
            'verify_url': verify_url, # Return URL for Simulation UI
            'email_sent': email_sent
        })"""

content = content.replace(old_code, new_code)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("registerSimple patched with email_sent flag!")
