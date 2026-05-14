import sys
import secrets

file_path = "backendold/Astro_backend/app/ServiceConfig/register.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_route = """

@app.route('/generateApiKey', methods=['POST'])
def generateApiKey():
    try:
        data = request.json
        dataInput = json.loads(decode(data['user']))
        user_id = dataInput['user_id']
        
        # Generate 32 char key
        import string
        import random
        alphabet = string.ascii_letters + string.digits
        new_key = ''.join(random.choices(alphabet, k=32))
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "UPDATE user SET apikey = %s WHERE user_id = %s"
        cursor.execute(sql, (new_key, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return updated user profile
        conn = mysql.connect()
        cursor = conn.cursor()                   
        sql_getdata = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(sql_getdata, user_id)
        user_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(user_data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        current_app.logger.error("Error generating API key:", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})

"""

if "def generateApiKey():" not in content:
    content += new_route
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Appended /generateApiKey route successfully.")
else:
    print("Route already exists.")
