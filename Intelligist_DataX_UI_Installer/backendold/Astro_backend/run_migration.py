import mysql.connector
import sys

def test_conn(host, user, password, db):
    print(f"Testing {host}...")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            connect_timeout=5,
            ssl_disabled=True
        )
        print(f"SUCCESS: Connected to {host}")
        cursor = conn.cursor()
        
        # Read the migration file
        with open('db_migration_v8.sql', 'r') as f:
            sql_script = f.read()
            
        print(f"Executing migration on {host}...")
        # Split script by semicolon if needed or just use multi=True
        for result in cursor.execute(sql_script, multi=True):
            if result.with_rows:
                result.fetchall()
        
        conn.commit()
        print(f"MIGRATION COMPLETE on {host}")
        conn.close()
        return True
    except Exception as e:
        print(f"FAILED on {host}: {str(e)}")
        return False

hosts = ['110.78.210.129', '10.20.31.32', 'localhost', '127.0.0.1']
user = 'administrator'
password = 'P@ssw0rd1234'
db = 'psu_backend'

for host in hosts:
    if test_conn(host, user, password, db):
        sys.exit(0)

print("All hosts failed.")
sys.exit(1)
