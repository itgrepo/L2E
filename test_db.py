from ServiceConfig import *
from ServiceConfig.bigdataservice import *

conn = get_oracle_connection('STG_DATAEXCHAGE')
cursor = conn.cursor()
sql = "SELECT column_name, data_type, nullable FROM user_tab_columns WHERE table_name = 'STG_EWE_COURSE' ORDER BY column_id"
cursor.execute(sql)
data = cursor.fetchall()
print(data[:2])
result = [{'name': row[0], 'type': row[1], 'nullable': 'YES' if row[2] == 'Y' else 'NO'} for row in data]
print(result[:2])
