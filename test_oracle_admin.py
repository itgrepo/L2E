import oracledb

config_dir = '/app/Wallet_L2EPRDDB'
dsn = 'l2eprddb_high'
user = 'ADMIN'

passwords_to_try = [
    'Coj@4321',
    'coj@4321',
    'COJ@4321',
    'coj@1234',
    'Coj@1234',
    '"Coj@4321"',
    'admin',
    'ADMIN',
    'Admin@123',
    'L2E@2024'
]

for pwd in passwords_to_try:
    try:
        conn = oracledb.connect(user=user, password=pwd, config_dir=config_dir, wallet_location=config_dir, wallet_password='Coj@4321', dsn=dsn)
        print(f"SUCCESS with password: {pwd}")
        conn.close()
        break
    except Exception as e:
        pass
else:
    print("ALL PASSWORDS FAILED")
