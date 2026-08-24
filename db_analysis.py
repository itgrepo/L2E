import subprocess
import json

def run_query(q):
    cmd = f"ssh -i ~/.ssh/ubuntuL2E.key -o StrictHostKeyChecking=no ubuntu@134.185.172.127 \"sudo docker exec datax_db_3003 mysql -u astro -ppassword123 datax_db_3003 -e '{q}'\""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

print("--- Duplicate Dataset IDs ---")
print(run_query("SELECT dataset_id, COUNT(*) as c FROM service WHERE dataset_id IS NOT NULL AND dataset_id != '' GROUP BY dataset_id HAVING c > 1;"))

print("\n--- Empty/Null Dataset IDs ---")
print(run_query("SELECT COUNT(*) FROM service WHERE dataset_id IS NULL OR dataset_id = '';"))

print("\n--- Distinct Data Sources ---")
print(run_query("SELECT DISTINCT data_source FROM service WHERE data_source IS NOT NULL AND data_source != '';"))
