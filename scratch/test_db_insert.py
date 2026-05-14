import pymysql
import sys

def test_insert():
    try:
        conn = pymysql.connect(
            host='110.78.210.128',
            user='root',
            password='ieat_pass',
            db='psu_backend',
            port=3307
        )
        cursor = conn.cursor()
        
        # 1. DESC user
        print("--- DESC user ---")
        cursor.execute("DESC user")
        for row in cursor.fetchall():
            print(row)
            
        # 2. Test Insert
        print("\n--- Testing Insert ---")
        username = "debug_user_" + str(pymysql.util.time.time())
        password = "debug_password"
        email = username + "@test.com"
        firstname = "Debug"
        lastname = "User"
        policy_id = 1
        organization = "Debug Org"
        
        sql = """INSERT INTO user (
                    username, password, email, firstname, lastname, 
                    job_title, previlage_id, status_id, status_account, 
                    national_id, national_id_mode, policy_id, usage_objective, 
                    last_update
                 ) VALUES (%s, %s, %s, %s, %s, '', 3, 4, 'active', %s, 1, %s, %s, CURRENT_TIMESTAMP)"""
        
        try:
            cursor.execute(sql, (username, password, email, firstname, lastname, username, policy_id, organization))
            print("Insert into user: SUCCESS")
        except Exception as e:
            print(f"Insert into user: FAILED - {e}")
            
        conn.close()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_insert()
