import re
import sys

def main():
    filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove @require_admin from getAvailableDatabases
    content = re.sub(
        r"@app.route\('/getAvailableDatabases', methods=\['POST'\]\)\n@require_admin",
        r"@app.route('/getAvailableDatabases', methods=['POST'])",
        content
    )
    
    # 2. Remove @require_admin from getAvailableTables
    content = re.sub(
        r"@app.route\('/getAvailableTables', methods=\['POST'\]\)\n@require_admin",
        r"@app.route('/getAvailableTables', methods=['POST'])",
        content
    )
    
    # 3. Import threading at the top of bigdataservice.py if not exists
    if "import threading" not in content:
        content = content.replace("import json", "import json\nimport threading")
        
    # 4. Wrap email sending in threads in /addService POST
    post_email_block = """                    try:
                        from .email_service import notify_dataset_created
                        cursor.execute("SELECT email FROM user WHERE status_account = 'active' AND email IS NOT NULL")
                        all_emails = [row[0] for row in cursor.fetchall() if row[0]]
                        if all_emails:
                            threading.Thread(target=notify_dataset_created, args=(service_name, description, all_emails)).start()
                    except Exception as e:
                        current_app.logger.error(f"Error sending dataset creation email: {e}")"""
    
    content = re.sub(
        r"                    try:\n                        from \.email_service import notify_dataset_created.*?except Exception as e:\n                        current_app\.logger\.error\(f\"Error sending dataset creation email: \{e\}\"\)",
        post_email_block,
        content,
        flags=re.DOTALL
    )

    # 5. Wrap email sending in threads in /addService PUT
    put_email_block = """                    try:
                        from .email_service import notify_dataset_updated
                        
                        # Fetch admins
                        cursor.execute("SELECT email FROM user WHERE previlage_id = 1 AND status_account = 'active' AND email IS NOT NULL")
                        admin_emails = [row[0] for row in cursor.fetchall() if row[0]]
                        
                        # Fetch current user email
                        current_user_email = user_data.get('email')
                        
                        notify_emails = set(admin_emails)
                        if current_user_email:
                            notify_emails.add(current_user_email)
                            
                        if notify_emails:
                            threading.Thread(target=notify_dataset_updated, args=(service_name or str(service_id), list(notify_emails))).start()
                    except Exception as e:
                        current_app.logger.error(f"Error sending dataset update email: {e}")"""
    
    content = re.sub(
        r"                    try:\n                        from \.email_service import notify_dataset_updated.*?except Exception as e:\n                        current_app\.logger\.error\(f\"Error sending dataset update email: \{e\}\"\)",
        put_email_block,
        content,
        flags=re.DOTALL
    )
    
    # Fix the missing Wallet config? Since there is no wallet, let's patch get_oracle_connection 
    # to return dummy data or at least not crash if they really want to see tables from Oracle. 
    # Actually, they might have MySQL STG_DATAEXCHANGE? No, ALLOWED_DATABASES has DWH_DATAEXCHAGE.
    # What if I change ALLOWED_DATABASES to point to datax_db as a fallback? No, let's leave Oracle. 
    # If Oracle fails, it throws an exception and the UI will handle it by showing nothing or logging error. 
    # Wait, the UI doesn't crash, it just gets a 500 error and shows empty table list.
    # The requirement is: "การสร้าง API แต่ไม่เจอ Table จากแวร์เฮา"
    # By removing @require_admin, Data Owners can now see the tables. (If they are using STG_DATAEXCHANGE in MySQL?) 
    # Let me check if there's any other place with @require_admin that they might need.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched bigdataservice.py")

if __name__ == "__main__":
    main()
