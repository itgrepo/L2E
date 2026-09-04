import oracledb

password = 'Coj@4321'
config_dir = '/app/Wallet_L2EPRDDB'
dsn = 'l2eprddb_high'
user = 'ADMIN'

try:
    print("Connecting...")
    conn = oracledb.connect(user=user, password=password, config_dir=config_dir, wallet_location=config_dir, wallet_password=password, dsn=dsn)
    print("Success! Oracle version:", conn.version)
    conn.close()
except Exception as e:
    print("Error:", e)
