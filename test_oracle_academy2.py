import oracledb

passwords = ['Coj@4321', 'coj@4321', 'COJ@4321', 'ACADEMY_APP_PROD', 'academy_app_prod', 'L2E@2024']
for pwd in passwords:
    try:
        conn = oracledb.connect(user='ACADEMY_APP_PROD', password=pwd, config_dir='/app/Wallet_L2EPRDDB', wallet_location='/app/Wallet_L2EPRDDB', wallet_password='Coj@4321', dsn='l2eprddb_high')
        print(f"SUCCESS with password {pwd}")
        conn.close()
        break
    except Exception as e:
        pass
else:
    print("ALL FAILED")
