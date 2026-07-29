import pymysql
import hashlib
import json
import os
import secrets
import string

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', '110.78.210.129'),
        user=os.environ.get('DB_USER', 'astro'),
        password=os.environ.get('DB_PASS', 'zjkoC]6p'),
        database=os.environ.get('DB_NAME', 'psu_backend'),
        cursorclass=pymysql.cursors.DictCursor
    )

def generate_public_key_id():
    alphabet = string.ascii_letters + string.digits
    return 'datax_' + ''.join(secrets.choice(alphabet) for i in range(12))

def migrate_credentials():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT credential_id, secret_key FROM api_credentials")
        rows = cursor.fetchall()
        for row in rows:
            cred_id = row['credential_id']
            secret_key = row['secret_key']
            
            # If already migrated (or secret_key is somehow missing), skip
            if not secret_key:
                continue
                
            public_key_id = generate_public_key_id()
            secret_hash = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
            key_last_four = secret_key[-4:] if len(secret_key) >= 4 else secret_key.ljust(4, '*')
            
            cursor.execute("""
                UPDATE api_credentials 
                SET public_key_id = %s, secret_hash = %s, key_last_four = %s 
                WHERE credential_id = %s
            """, (public_key_id, secret_hash, key_last_four, cred_id))
        
        conn.commit()
        print(f"Migrated {len(rows)} credentials successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    migrate_credentials()
