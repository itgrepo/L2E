from flask import Flask, request, jsonify, send_from_directory, abort
import os
from . import app, mysql

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

@app.route('/downloadFile/<int:service_id>', methods=['GET'])
def downloadFile(service_id):
    try:
        # Default to main data file
        file_type = request.args.get('type', 'data')
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        col = 'file_path'
        if file_type == 'dictionary':
            col = 'data_dictionary_path'
        elif file_type == 'sampling':
            col = 'data_sampling_path'
        elif file_type == 'excel':
            col = 'excel_file_path'
            
        sql = f"SELECT {col} FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0]:
            file_name = result[0]
            if os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True)
            else:
                return jsonify({"status": "File not found on server"}), 404
        else:
            return jsonify({"status": "No file associated with this dataset"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500


@app.route('/downloadRequestMou/<int:request_id>', methods=['GET'])
def downloadRequestMou(request_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT mou_file_path, mou_filename FROM dataset_permission_requests WHERE request_id = %s"
        cursor.execute(sql, (request_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0]:
            file_name = result[0]
            if os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                # If attachment filename is provided, pass download_name / attachment_filename
                try:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, download_name=result[1] or file_name)
                except TypeError:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, attachment_filename=result[1] or file_name)
            else:
                return jsonify({"status": "File not found on server"}), 404
        else:
            return jsonify({"status": "No attached file found for this request"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500

