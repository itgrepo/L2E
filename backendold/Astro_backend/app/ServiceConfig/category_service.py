from ServiceConfig import app, mysql, toJson, platform_decode, safe_json_loads, checkUserIsAdmin
from flask import request, jsonify
import json

@app.route('/getCategories', methods=['POST'])
def getCategories():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT category_id as id, category_name as name FROM category"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/addCategory', methods=['POST'])
def addCategory():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        name = dataInput.get('name')
        if not name:
            return jsonify({"status": "Category name is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "INSERT INTO category (category_name) VALUES (%s)"
        cursor.execute(sql, (name,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Category created'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/updateCategory', methods=['POST'])
def updateCategory():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        cat_id = dataInput.get('id')
        name = dataInput.get('name')

        if not cat_id or not name:
            return jsonify({"status": "Category ID and name are required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "UPDATE category SET category_name = %s WHERE category_id = %s"
        cursor.execute(sql, (name, cat_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Category updated'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/deleteCategory', methods=['POST'])
def deleteCategory():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        cat_id = dataInput.get('id')

        if not cat_id:
            return jsonify({"status": "Category ID is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if category is used in service table
        sql_check = "SELECT COUNT(*) FROM service WHERE category = (SELECT category_name FROM category WHERE category_id = %s)"
        cursor.execute(sql_check, (cat_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
             return jsonify({"status": "Cannot delete category being used by datasets"})

        sql = "DELETE FROM category WHERE category_id = %s"
        cursor.execute(sql, (cat_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Category deleted'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/retrieveCategories', methods=['GET'])
def retrieveCategories():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT category_id as id, category_name as name FROM category"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/retrieveSubCategories', methods=['GET'])
def retrieveSubCategories():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Create table if not exists for minimal setup
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sub_category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(255) NOT NULL,
            sub_category_name VARCHAR(255) NOT NULL
        )
        """)
        
        sql = "SELECT category_name, sub_category_name FROM sub_category"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/addSubCategory', methods=['POST'])
def addSubCategory():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user')) if dataInput.get('user') else None
        user_data = safe_json_loads(decoded_user) if decoded_user else None

        # Minimal check or allow if needed, matching existing
        category_name = dataInput.get('category_name')
        sub_category_name = dataInput.get('sub_category_name')

        if not category_name or not sub_category_name:
            return jsonify({"status": "Category and Sub-Category names are required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sub_category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(255) NOT NULL,
            sub_category_name VARCHAR(255) NOT NULL
        )
        """)
        
        # Check duplicate
        cursor.execute("SELECT COUNT(*) FROM sub_category WHERE category_name=%s AND sub_category_name=%s", (category_name, sub_category_name))
        if cursor.fetchone()[0] == 0:
            sql = "INSERT INTO sub_category (category_name, sub_category_name) VALUES (%s, %s)"
            cursor.execute(sql, (category_name, sub_category_name))
            conn.commit()
            
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Sub-category created'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})
