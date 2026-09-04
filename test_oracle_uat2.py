import oracledb

password = 'Coj@4321'
config_dir = '/app/Wallet_L2EPRDDB'
dsn = 'l2eprddb_high'

users_to_try = ['ADMIN', 'L2E', 'L2EPRDDB', 'L2E_PRD_DB']

for user in users_to_try:
    try:
        print(f"Connecting as {user}...")
        conn = oracledb.connect(user=user, password=password, config_dir=config_dir, wallet_location=config_dir, wallet_password=password, dsn=dsn)
        print("Success! Oracle version:", conn.version)
        conn.close()
        break
    except Exception as e:
        print("Error:", e)
