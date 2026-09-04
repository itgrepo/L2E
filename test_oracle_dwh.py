import oracledb

wallet_dir = '/app/Wallet_L2EPRDDB'
dsn = 'l2eprddb_high'
wallet_pwd = 'Coj@4321'
db_pwd = 'GoU8iFg24y90r243whrefWLq!'

users = ['DWH_DATAEXCHAGE', 'STG_DATAEXCHAGE']

for u in users:
    try:
        conn = oracledb.connect(user=u, password=db_pwd, config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password=wallet_pwd, dsn=dsn)
        print(f"SUCCESS with user: {u}")
        conn.close()
    except Exception as e:
        print(f"FAILED {u}: {e}")
