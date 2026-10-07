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
        
        sql = "SELECT file_path, excel_file_path, data_dictionary_path, data_sampling_path FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            file_path_val, excel_path_val, dict_path_val, samp_path_val = result
            file_name = None
            if file_type == 'dictionary':
                file_name = dict_path_val
            elif file_type == 'sampling':
                file_name = samp_path_val
            elif file_type == 'excel':
                file_name = excel_path_val or file_path_val
            else:
                file_name = file_path_val or excel_path_val

            if file_name and os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True)
            elif file_name:
                return jsonify({"status": "File not found on server"}), 404
            else:
                return jsonify({"status": "No file associated with this dataset"}), 404
        else:
            return jsonify({"status": "Dataset not found"}), 404
            
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

