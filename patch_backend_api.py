import sys

file_path = "backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# PATCH 1: Extract api_enabled from forms
target1 = """                geo_position_accuracy = request.form.get('geo_position_accuracy')
                geo_reference_time = request.form.get('geo_reference_time')
                geo_published_date = request.form.get('geo_published_date')"""

replacement1 = """                geo_position_accuracy = request.form.get('geo_position_accuracy')
                geo_reference_time = request.form.get('geo_reference_time')
                geo_published_date = request.form.get('geo_published_date')
                api_enabled_raw = request.form.get('api_enabled')
                api_enabled = 1 if api_enabled_raw in ['true', '1', True] else (0 if api_enabled_raw in ['false', '0', False] else None)"""

# PATCH 2: Append to update query
target2 = """                    if geo_reference_time is not None: fields.append("geo_reference_time = %s"); values.append(geo_reference_time)
                    if geo_published_date is not None: fields.append("geo_published_date = %s"); values.append(geo_published_date)"""

replacement2 = """                    if geo_reference_time is not None: fields.append("geo_reference_time = %s"); values.append(geo_reference_time)
                    if geo_published_date is not None: fields.append("geo_published_date = %s"); values.append(geo_published_date)
                    if api_enabled is not None: fields.append("api_enabled = %s"); values.append(api_enabled)"""

# PATCH 3: Add new endpoint /dataapi/api/v1/<dataset_id>
new_endpoint = """
@app.route('/dataapi/api/v1/<dataset_id>', methods=['GET'])
def get_dataset_api(dataset_id):
    try:
        apikey = request.args.get('apikey')
        if not apikey:
            return jsonify({'status': 'error', 'message': 'Missing apikey parameter'}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Validate API Key
        sql_user = "SELECT user_id, firstname, lastname FROM user WHERE apikey = %s"
        cursor.execute(sql_user, (apikey,))
        user_data = cursor.fetchall()
        
        if not user_data:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Invalid API Key'}), 403
            
        # 2. Check Dataset and API Access
        sql_service = "SELECT service_name, api_enabled FROM service WHERE dataset_id = %s"
        cursor.execute(sql_service, (dataset_id,))
        dataset_data = cursor.fetchall()
        
        if not dataset_data:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Dataset not found'}), 404
            
        if not dataset_data[0][1]: # api_enabled is False/0
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'API access is disabled for this dataset'}), 403
            
        cursor.close()
        conn.close()
        
        # 3. Return Mock JSON Data mimicking M-Society Portal row outputs
        import datetime
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return jsonify({
            'status': 'success',
            'dataset_id': dataset_id,
            'dataset_name': dataset_data[0][0],
            'total_rows': 2,
            'offset': 0,
            'rows': [
                {
                    "id": f"{dataset_id}-row1",
                    "data": {
                        "value": 100.50,
                        "updated_at": timestamp
                    }
                },
                {
                    "id": f"{dataset_id}-row2",
                    "data": {
                        "value": 250.75,
                        "updated_at": timestamp
                    }
                }
            ]
        })
    except Exception as e:
        current_app.logger.error("Error in data API:", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
"""

if target1 in content and target2 in content:
    content = content.replace(target1, replacement1)
    content = content.replace(target2, replacement2)
    
    # Append endpoint before last line
    import re
    # Just append to the end of file (assuming we aren't at the very end of app scope)
    # wait, there's `app.route`s everywhere. Let's just append to end of file, or before `if __name__ == '__main__':`
    content += new_endpoint
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("bigdataservice.py patched successfully.")
else:
    print("Failed to find targets.")
