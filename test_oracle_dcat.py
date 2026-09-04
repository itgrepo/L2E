import oracledb
try:
    conn = oracledb.connect(user='DCAT_ADMIN', password='Coj@4321', config_dir='/app/Wallet_L2EPRDDB', wallet_location='/app/Wallet_L2EPRDDB', wallet_password='Coj@4321', dsn='l2eprddb_high')
    print("SUCCESS: DCAT_ADMIN")
    conn.close()
except Exception as e:
    print("Error:", e)
