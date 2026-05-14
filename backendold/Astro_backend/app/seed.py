import hmac
import hashlib
import pymysql
import sys

import os

# Database configuration (matching __init__.py)
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '110.78.210.129'),
    'user': os.environ.get('DB_USER', 'astro'),
    'password': os.environ.get('DB_PASS', 'zjkoC]6p'),
    'db': os.environ.get('DB_NAME', 'psu_backend'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Password encryption settings (matching login.py)
HMAC_KEY = 'e9NHdT3GU6wBdWlw3RTqvrShGzyerRl4BaMhFeUI3v4j6U0opW5a19HQHDAHHCrhYXq8oG6D'.encode("utf-8")

def encrypt_password(raw_password):
    return hmac.new(HMAC_KEY, raw_password.encode("utf-8"), hashlib.sha256).hexdigest()

def seed():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            print("Connecting to database...")
            
            # 1. Create Default Admin User
            username = 'testadmin'
            password = 'password123'
            encrypted = encrypt_password(password)
            email = 'admin@example.com'
            firstname = 'System'
            lastname = 'Administrator'
            
            # 0. Clean old test data
            print("Cleaning old test data...")
            cursor.execute("DELETE FROM user_activity WHERE user_id IN (SELECT user_id FROM user WHERE username = %s)", (username,))
            cursor.execute("DELETE FROM DataField WHERE national_id = '1234567890123'")
            cursor.execute("DELETE FROM user WHERE username = %s", (username,))
            
            print(f"Creating user: {username}...")
            # Insert into user table
            sql_user = """
            INSERT INTO user (username, password, email, firstname, lastname, national_id, national_id_book, national_id_mode, status_id, status_account, previlage_id, job_title)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_user, (username, password, email, firstname, lastname, '1234567890123', 'PASS123', 1, 1, 'active', 1, 'Admin'))
            user_id = cursor.lastrowid
            
            # Insert into user_activity table
            sql_activity = """
            INSERT INTO user_activity (user_id, login_status, login_respond, create_date, status_account, password, emailnews)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_activity, (user_id, 0, 0, 0, '1', password, '-'))
            
            # Insert into DataField (Required by login query)
            sql_datafield = """
            INSERT INTO DataField (national_id, national_id_book, sublevel_id, expiration)
            VALUES (%s, %s, %s, '2099-12-31')
            """
            cursor.execute(sql_datafield, ('1234567890123', 'PASS123', 1))
            
            # Ensure sublevel_master exists
            cursor.execute("SELECT sublevel_id FROM sublevel_master WHERE sublevel_id = 1")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO sublevel_master (sublevel_id, Level_Master_id) VALUES (1, 1)")

            print(f"User {username} created successfully.")

            # 2. Create Sample Services (Catalog)
            print("Creating sample services...")
            sample_services = [
                ('Demographic Data 2024', 'Population statistics by region and age group.', 'Public', 'Active'),
                ('Import/Export Stats', 'Monthly trade data for key commodities.', 'Private', 'Active'),
                ('Weather Trends', 'Historical weather data for the last 10 years.', 'Public', 'Active')
            ]
            
            for name, desc, access, status in sample_services:
                cursor.execute("SELECT service_id FROM service WHERE service_name = %s", (name,))
                if not cursor.fetchone():
                    sql_service = "INSERT INTO service (service_name, description, access_type, status) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_service, (name, desc, access, status))
                    print(f"Service '{name}' added.")

            connection.commit()
            print("Seeding completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    seed()
