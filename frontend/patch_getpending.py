# coding=utf-8
import codecs
import re

with codecs.open('ServiceConfig/bigdataservice.py', 'r', 'utf-8') as f:
    content = f.read()

# Replace get_pending_dataset_requests SQL
old_sql_1 = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            u.username, u.firstname, u.lastname, u.email,
                            s.service_name, s.dataset_id
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     JOIN service s ON r.service_id = s.service_id
                     ORDER BY r.created_at DESC"""

new_sql_1 = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            u.username, u.firstname, u.lastname, u.email,
                            org.org_name as organization,
                            s.service_name, s.dataset_id
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     LEFT JOIN organization org ON u.org_id = org.org_id
                     JOIN service s ON r.service_id = s.service_id
                     ORDER BY r.created_at DESC"""

old_sql_2 = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            u.username, u.firstname, u.lastname, u.email,
                            s.service_name, s.dataset_id
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     JOIN service s ON r.service_id = s.service_id
                     WHERE r.status = %s
                     ORDER BY r.created_at DESC"""

new_sql_2 = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            u.username, u.firstname, u.lastname, u.email,
                            org.org_name as organization,
                            s.service_name, s.dataset_id
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     LEFT JOIN organization org ON u.org_id = org.org_id
                     JOIN service s ON r.service_id = s.service_id
                     WHERE r.status = %s
                     ORDER BY r.created_at DESC"""

content = content.replace(old_sql_1, new_sql_1)
content = content.replace(old_sql_2, new_sql_2)

with codecs.open('ServiceConfig/bigdataservice.py', 'w', 'utf-8') as f:
    f.write(content)
