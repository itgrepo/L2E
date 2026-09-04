import oracledb

wallet_dir = '/app/Wallet_L2EPRDDB'
dsn = 'l2eprddb_high'
wallet_pwd = 'Coj@4321'
db_pwd = 'GoU8iFg24y90r243whrefWLq!'

try:
    conn = oracledb.connect(user='ACADEMY_APP_PROD', password=db_pwd, config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password=wallet_pwd, dsn=dsn)
    print("SUCCESS with ACADEMY_APP_PROD in L2EPRDDB!")
    conn.close()
except Exception as e:
    print(f"FAILED ACADEMY: {e}")
