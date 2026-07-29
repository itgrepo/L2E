from flask import Flask, request, jsonify, current_app, abort, send_from_directory, send_file, redirect
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api
from werkzeug.contrib.fixers import ProxyFix
from flask import Response
import geoip2.database

from datetime import datetime
import sys, errno
import os
import glob
import shutil
import pytz
import codecs
import string
# import pymssql
# import pymongo
# import gridfs
import json
import csv
import base64
import urllib
import io
from bson.json_util import dumps
from flask_pymongo import PyMongo
# from pyhive import hive
# import psycopg2
import pyotp
import time
from random import randint
# from importlib import reload
import re

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# app4 = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['xls', 'xlsm', 'xlsx', 'csv', 'txt', 'xml'])

# CORS(app, resources={r"/api/*": {"origins": ["http://10.252.3.228/*"]}})
# CORS(app, origins=['http://203.154.58.142/*', 'http://localhost/*'])
# CORS(app2, origins=['http://203.154.58.142/*', 'http://localhost/*'])
CORS(app)
api = Api(app)


app.config['MYSQL_DATABASE_USER'] = os.environ.get('DB_USER', 'astro')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('DB_PASS', 'zjkoC]6p')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('DB_NAME', 'psu_backend')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('DB_HOST', '110.78.210.129')
app.config['MYSQL_DATABASE_PORT'] = int(os.environ.get('DB_PORT', 3306))

mysql = MySQL()
mysql.init_app(app)


def logAction(user_id, path, log, type):
    ip = request.headers.get('X-FORWARDED-FOR', None)
    if ip:
        ip_address = ip.split(',')
    else:
        ip_address = [request.remote_addr or '127.0.0.1']
    ip_check = ip_address[0].split('.')
    if ip_check[0] != "192":
        conn = mysql.connect()
        cursor = conn.cursor()
        #reader = geoip2.database.Reader('/app/resources/GeoLite2-City_20190903/GeoLite2-City.mmdb')
        #--------------------------------------------------#
        try :
            #response = reader.city(str(ip_address[0]))
        # sql = "INSERT INTO log VALUES (NULL, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
            sql = "INSERT INTO log VALUES (NULL, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)"
            cursor.execute(sql, (user_id, ip_address[0], path, log, type, "None"))
        # cursor.execute(sql, (user_id, ip_address[0], path, log, type))
        # cursor.execute(sql, (user_id, '203.xxx', path, log, type))
        except :
            # ! ถ้าไม่สามารถตรวจหาประเทศจาก IP ได้ จะให้ประเทศเป็น None
            sql = "INSERT INTO log VALUES (NULL, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)"
            cursor.execute(sql, (user_id, ip_address[0], path, log, type, "None"))
        #--------------------------------------------------#
        conn.commit()
        cursor.close()
        return 'success'

    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO log VALUES (NULL, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)"
        cursor.execute(sql, (user_id, ip_address[0], path, log, type, "None"))
        # cursor.execute(sql, (user_id, ip_address[0], path, log, type))
        # cursor.execute(sql, (user_id, '203.xxx', path, log, type))
        conn.commit()
        cursor.close()
        return 'success'

def toJson(data,columns):
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    return results

def decode(data):
    return base64.b64decode(data[:-5][::-1])

def platform_decode(data):
    if not data:
        return ""
    try:
        # Standard decode pattern used in this project
        decoded = base64.b64decode(data[:-5][::-1]).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Decode error: {e}")
        return ""

def safe_json_loads(data):
    if not data:
        return {}
    try:
        return json.loads(data)
    except:
        return {}

def checkUserIsAdmin(user_data):
    conn = mysql.connect()
    cursor = conn.cursor()
    # sql_check_Permission = "SELECT previlage_id FROM user WHERE user_id = %s AND username = %s AND email = %s AND status_id != 7"
    # cursor.execute(sql_check_Permission, (user_data['user_id'],user_data['username'],user_data['email']))
    sql_check_Permission = "SELECT previlage_id FROM user WHERE user_id = %s AND username = %s AND status_id != 7"
    cursor.execute(sql_check_Permission, (user_data['user_id'],user_data['username']))
    data_check_Permission = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result_check_Permission = toJson(data_check_Permission, columns)
    conn.commit()
    cursor.close()
    if len(result_check_Permission) != 0 :
        if str(result_check_Permission[0]['previlage_id']) not in ['3']: # previlage_id = 1 is Admin
            return True #user is admin
        else :
            return False #user not admin
    else : #not found user
        return False

from functools import wraps
def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            dataInput = request.json if request.is_json else request.form
            if not dataInput:
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            
            user_str = dataInput.get('user')
            if not user_str:
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            
            user_data = safe_json_loads(platform_decode(user_str))
            if not user_data or not user_data.get('user_id'):
                return jsonify({"status": "error", "message": "Invalid user payload"}), 401
                
            if not checkUserIsAdmin(user_data):
                return jsonify({"status": "error", "message": "Admin access required"}), 403
                
            request.current_user = user_data
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"status": "error", "message": "Authentication error"}), 401
    return decorated
    
    #--------------------------------------------------------------#
def createSecretKeyTwoFactor(username,option):
    try:
        #New secret key
        conn = mysql.connect()
        cursor = conn.cursor()
        result = ''.join([i for i in username if not i.isdigit()])
        result = ''.join(e for e in result if e.isalnum())
        username_upper = result.upper()
        unix = str(int(time.time()))
        value = str(randint(2, 7))
        unix = unix.replace("1",value).replace("8",value).replace("9",value).replace("0",value)
        # print(unix)
        secret_key = pyotp.random_base32(16,'%s%s234567'%(username_upper,unix))
        # print("this is key : ",secret_key)
    #         print(secret_key)
        sql1 = """SELECT secret_key from user_secret_key where secret_key = %s"""
        cursor.execute(sql1,(secret_key))
        secret_key_result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        secret_key_data = toJson(secret_key_result, columns)
        # print(secret_key_data)
            #================================ New feature add secret_key to table ==================================
            #================== Secret key manage for exist user===================
        if(option == 1):
            if len(secret_key_data) == 0:
                # print(secret_key)
                sql1 = """SELECT user_secret_key.user_id FROM user_secret_key 
                            LEFT JOIN user
                                ON user_secret_key.user_id = user.user_id
                            WHERE username = %s"""
                cursor.execute(sql1,(username))
                user_secret_key_result = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                user_secret_key_data = toJson(user_secret_key_result, columns)
                # print(user_secret_key_data)
                if len(user_secret_key_data) == 0:
                    sql1 = """SELECT user_id from user where username = %s AND status_id != 7"""
                    cursor.execute(sql1,(username))
                    user_id_secret_key_result = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    user_id_secret_key = toJson(user_id_secret_key_result, columns)
                    sql2 = """INSERT INTO user_secret_key (user_id,secret_key,secret_key_status) VALUES (%s,%s,%s)"""
                    cursor.execute(sql2,(user_id_secret_key[0]['user_id'],secret_key,'active'))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    stringToQR = pyotp.totp.TOTP(secret_key).provisioning_uri(username, issuer_name="bigdataplatform.customs.net")
                    return stringToQR
                elif len(user_secret_key_data) != 0:
                    # conn.commit()
                    sql2 = """UPDATE user_secret_key
                                SET secret_key = %s
                                WHERE user_id = %s;"""
                    cursor.execute(sql2,(secret_key,user_secret_key_data[0]['user_id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    stringToQR = pyotp.totp.TOTP(secret_key).provisioning_uri(username, issuer_name="bigdataplatform.customs.net")
                    # print(stringToQR)
                    return stringToQR
                else :
                    return("Error")
            elif len(secret_key_data) != 0:
                createSecretKeyTwoFactor(username,option= 1)
            #================== Secret key manage for new user===================
        elif(option == 2):
            if len(secret_key_data) == 0:
                sql1 = """SELECT user_id from user where username = %s AND status_id != 7"""
                cursor.execute(sql1,(username))
                user_id_secret_key_result = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                user_id_secret_key = toJson(user_id_secret_key_result, columns)
                sql2 = """INSERT INTO user_secret_key (user_id,secret_key,secret_key_status) VALUES (%s,%s,%s)"""
                cursor.execute(sql2,(user_id_secret_key[0]['user_id'],secret_key,'active'))
                conn.commit()
                cursor.close()
                conn.close()
                stringToQR = pyotp.totp.TOTP(secret_key).provisioning_uri(username, issuer_name="bigdataplatform.customs.net")
                return stringToQR

            elif len(secret_key_data) != 0:
                createSecretKeyTwoFactor(username,option = 2)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return ("Error: " + str(e)+"Line number "+line_number)
        # return("Error")
#------------#
def check_email_format(email):
    if isinstance(email,str) : #check type [str] 
        regex_check_email_format = "^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
        if not re.match(regex_check_email_format ,email):
            return False
        else : 
            return True
    else :
        return False