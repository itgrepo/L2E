from app import app
with app.test_client() as c:
    response = c.post('/getTableColumns', json={"db_name":"STG_DATAEXCHAGE", "table_name":"STG_EWE_COURSE"})
    print(response.get_json())
