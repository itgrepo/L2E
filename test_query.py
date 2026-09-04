import oracledb

wallet_dir = '/app/Wallet_L2EPRDDWH'
dsn = 'l2eprddwh_high'
db_pwd = 'GoU8iFg24y90r243whrefWLq!'

try:
    conn = oracledb.connect(user='DWH_DATAEXCHAGE', password=db_pwd, config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password=db_pwd, dsn=dsn)
    cursor = conn.cursor()
    
    # Get the first table name
    cursor.execute("SELECT table_name FROM user_tables FETCH FIRST 1 ROWS ONLY")
    row = cursor.fetchone()
    
    if row:
        table_name = row[0]
        print(f"Table found: {table_name}")
        
        # Query 5 rows from this table
        cursor.execute(f"SELECT * FROM {table_name} FETCH FIRST 5 ROWS ONLY")
        columns = [col[0] for col in cursor.description]
        print(f"Columns: {columns}")
        
        for data in cursor.fetchall():
            print(data)
    else:
        print("No tables found in this schema.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
