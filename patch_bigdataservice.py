import os
import re

file_path = 'backendold/Astro_backend/app/ServiceConfig/bigdataservice.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update the POST form extraction
post_extract_target = "                data_source = request.form.get('data_source', '')"
post_extract_repl = """                data_source = request.form.get('data_source', '')
                
                # Wave 2 Masters
                l2e_group_id_raw = request.form.get('l2e_group_id', '')
                l2e_group_id = int(l2e_group_id_raw) if l2e_group_id_raw else None
                source_system_id_raw = request.form.get('source_system_id', '')
                source_system_id = int(source_system_id_raw) if source_system_id_raw else None"""
content = content.replace(post_extract_target, post_extract_repl)

# 2. Update the POST validate call
post_validate_target = "                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type)"
post_validate_repl = "                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type, l2e_group_id, source_system_id, dataset_id)"
content = content.replace(post_validate_target, post_validate_repl, 1) # Replace first occurence (POST)

# 3. Update POST INSERT query
post_insert_target = """                        geo_reference_time, geo_published_date
                    ) VALUES("""
post_insert_repl = """                        geo_reference_time, geo_published_date,
                        l2e_group_id, source_system_id
                    ) VALUES("""
content = content.replace(post_insert_target, post_insert_repl)

# 4. Update POST INSERT values placeholder
post_val_target = """%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
post_val_repl = """%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
content = content.replace(post_val_target, post_val_repl)

# 5. Update POST cursor.execute arguments
post_exec_target = """                        geo_reference_time, geo_published_date
                    ))"""
post_exec_repl = """                        geo_reference_time, geo_published_date,
                        l2e_group_id, source_system_id
                    ))"""
content = content.replace(post_exec_target, post_exec_repl)

# 6. Update the PUT form extraction
put_extract_target = "                data_source = request.form.get('data_source')"
put_extract_repl = """                data_source = request.form.get('data_source')
                
                # Wave 2 Masters
                l2e_group_id_raw = request.form.get('l2e_group_id')
                l2e_group_id = int(l2e_group_id_raw) if l2e_group_id_raw else None
                source_system_id_raw = request.form.get('source_system_id')
                source_system_id = int(source_system_id_raw) if source_system_id_raw else None"""
content = content.replace(put_extract_target, put_extract_repl)

# 7. Update the PUT validate call
put_validate_target = "                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type)"
put_validate_repl = "                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type, l2e_group_id, source_system_id, dataset_id)"
content = content.replace(put_validate_target, put_validate_repl) # Replace all remaining occurrences

# 8. Update the PUT field append
put_append_target = "                    if data_source is not None: fields.append(\"data_source = %s\"); values.append(data_source)"
put_append_repl = """                    if data_source is not None: fields.append("data_source = %s"); values.append(data_source)
                    if request.form.get('l2e_group_id') is not None: fields.append("l2e_group_id = %s"); values.append(l2e_group_id)
                    if request.form.get('source_system_id') is not None: fields.append("source_system_id = %s"); values.append(source_system_id)"""
content = content.replace(put_append_target, put_append_repl)

# 9. In `getService`, `retrieveService`, `retrieveServiceByOrg` we need to return `l2e_group_id` and `source_system_id`.
# Actually, the user asked for:
# "Response คืน code และ display name" for L2E Group. Let's just return IDs for now in the main response and let Frontend match with master, OR do a JOIN in `retrieveService`.
# We'll use `multi_replace_file_content` if we need to modify SQLs in `retrieveService`.

with open(file_path, 'w') as f:
    f.write(content)
print("Patched!")
