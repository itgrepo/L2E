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
