import subprocess
import requests
import time
import json
import uuid

# Configuration
TEST_DB_CONTAINER = "astro_db"
API_BASE_URL = "http://127.0.0.1:7001/dataapi/api/v1"
MOCK_DATASET_ID = "test_auto_scope_123"

def run_sql(sql_cmd):
    # Runs SQL against the MariaDB container directly
    cmd = [
        "/usr/local/bin/docker-compose", "exec", "-T", "db",
        "mysql", "-u", "root", "-prootpassword", "psu_backend"
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(input=sql_cmd.encode('utf-8'))
    if process.returncode != 0:
        print(f"SQL Error: {err.decode('utf-8')}")
    return out.decode('utf-8')

print("=== 🚀 Starting Automated API Behavior Test ===\n")

print("1. [Setup] Injecting Mock Dataset and Rules into Database (via SQL)")

# We use the existing 'user' table as a fallback to query data so we don't have to create mock data tables
setup_sql = f"""
-- Delete old mock if exists
DELETE FROM service WHERE dataset_id = '{MOCK_DATASET_ID}';

-- Create a mock Service that reads from 'user' table with Scope enabled
INSERT INTO service 
  (service_name, dataset_id, api_enabled, api_type, api_db_name, api_source_type, api_source_name, api_response_fields)
VALUES 
  ('Mock Scope API', '{MOCK_DATASET_ID}', 1, 'scope', 'psu_backend', 'table', 'user', '["username", "firstname"]');

-- Get the inserted service ID
SET @svc_id = LAST_INSERT_ID();

-- Give us 3 users
INSERT IGNORE INTO user (user_id, username, password) VALUES (997, 'user_expired', 'xxx');
INSERT IGNORE INTO user (user_id, username, password) VALUES (998, 'user_revoked', 'xxx');
INSERT IGNORE INTO user (user_id, username, password) VALUES (999, 'admin_mock', 'xxx');

-- Clean up old keys if existing
DELETE FROM api_credentials WHERE service_id = @svc_id;

-- Key 1: VALID SCOPED KEY
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@svc_id, 999, 'valid_key_123', 'active', '2030-01-01 00:00:00');
SET @cred_1 = LAST_INSERT_ID();

-- Add scope for Key 1
INSERT INTO api_scopes (credential_id, scope_json) 
VALUES (@cred_1, '{{"username": ["admin_mock"]}}');

-- Key 2: EXPIRED KEY
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@svc_id, 997, 'expired_key_123', 'active', '2000-01-01 00:00:00');

-- Key 3: REVOKED KEY
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@svc_id, 998, 'revoked_key_123', 'revoked', '2030-01-01 00:00:00');

"""

run_sql(setup_sql)

print("✅ Setup complete. Keys generated.\n")
print("-" * 50)


print("2. [Test Action] Calling API with EXPIRED Key")
print("Target: EXPECTING 403 Forbidden")
res = requests.get(f"{API_BASE_URL}/{MOCK_DATASET_ID}?apikey=expired_key_123")
print(f"-> Status Code: {res.status_code}")
try:
    print(f"-> Response: {res.json()}")
    resp_text = res.json()
except:
    print(f"-> Response (Text): {res.text}")
    resp_text = {}
if res.status_code in [403, 401] and ("expired" in str(resp_text).lower() or "invalid" in str(resp_text).lower()):
    print("✅ TEST PASSED")
else:
    print("❌ TEST FAILED")

print("-" * 50)


print("3. [Test Action] Calling API with REVOKED (Paused) Key")
print("Target: EXPECTING 403 Forbidden")
res = requests.get(f"{API_BASE_URL}/{MOCK_DATASET_ID}?apikey=revoked_key_123")
print(f"-> Status Code: {res.status_code}")
try:
    print(f"-> Response: {res.json()}")
    resp_text = res.json()
except:
    print(f"-> Response (Text): {res.text}")
    resp_text = {}
if res.status_code in [403, 401] and "revok" in str(resp_text).lower():
    print("✅ TEST PASSED")
else:
    print("❌ TEST FAILED")

print("-" * 50)


print("4. [Test Action] Calling API with VALID Scope Key")
print("Target: EXPECTING 200 OK & Data must be filtered strictly by Scope (only 'admin_mock' row should appear)")
res = requests.get(f"{API_BASE_URL}/{MOCK_DATASET_ID}?apikey=valid_key_123")
print(f"-> Status Code: {res.status_code}")
try:
    data = res.json()
except:
    data = res.text
print(f"-> Response Data: {data}")

passed = False
if res.status_code == 200:
    rows = data.get('rows', [])
    if isinstance(rows, list) and len(rows) > 0:
        # Check if row-level security worked
        all_admins = all(r.get('username') == 'admin_mock' for r in rows)
        if all_admins:
            passed = True

if passed:
    print("✅ TEST PASSED")
else:
    print("❌ TEST FAILED")

print("-" * 50)

print("5. [Cleanup] Validating that the LOG TABLE recorded these events")
log_check = run_sql(f"SELECT log_detail, path FROM log WHERE type='API' ORDER BY log_id DESC LIMIT 3;")
print("-> Recent logs from Database:")
print(log_check)
print("✅ Automated Testing Finished.")
