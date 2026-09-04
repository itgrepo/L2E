import oracledb

try:
    conn = oracledb.connect(user='ACADEMY_APP_PROD', password='Coj@4321', config_dir='/app/Wallet_L2EPRDDB', wallet_location='/app/Wallet_L2EPRDDB', wallet_password='Coj@4321', dsn='l2eprddb_high')
    print("SUCCESS: ACADEMY_APP_PROD")
    
    # Let's list some tables
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM all_tables WHERE owner = 'ACADEMY_OWNER_PROD' FETCH FIRST 10 ROWS ONLY")
    tables = cursor.fetchall()
    print("Tables found:", tables)
    conn.close()
except Exception as e:
    print("Error:", e)
