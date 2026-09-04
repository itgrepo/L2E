import oracledb

wallet_dir = '/app/Wallet_L2EPRDDWH'
dsn = 'l2eprddwh_high'
db_pwd = 'GoU8iFg24y90r243whrefWLq!'

try:
    conn = oracledb.connect(user='DWH_DATAEXCHAGE', password=db_pwd, config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password=db_pwd, dsn=dsn)
    print("SUCCESS with wallet_password = db_pwd!")
    conn.close()
except Exception as e:
    print(f"FAILED with wallet_password = db_pwd: {e}")

try:
    conn = oracledb.connect(user='DWH_DATAEXCHAGE', password=db_pwd, config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password='Coj@4321', dsn=dsn)
    print("SUCCESS with wallet_password = Coj@4321!")
    conn.close()
except Exception as e:
    print(f"FAILED with wallet_password = Coj@4321: {e}")
