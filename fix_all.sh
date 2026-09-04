#!/bin/bash

# Remove platform_decode and safe_json_loads from all files that redefine them
for file in /app/ServiceConfig/register.py /app/ServiceConfig/bigdataservice.py /app/ServiceConfig/group_service.py /app/ServiceConfig/access_service.py; do
    # Delete from 'def platform_decode' to the next 'def ' or end of file (wait, awk is safer)
    awk '/def platform_decode\(data\):/{flag=1; next} /def safe_json_loads\(data\):/{flag=1; next} /^def /{flag=0} !flag' $file > ${file}.tmp && mv ${file}.tmp $file
done

# Update decode() in __init__.py
sed -i -e '/def decode(data):/,+1c\
def decode(data):\
    try:\
        from itsdangerous import URLSafeTimedSerializer\
        import json\
        auth_serializer = URLSafeTimedSerializer("intelligist-datax-secure-secret-key-2026")\
        user_dict = auth_serializer.loads(data, max_age=86400)\
        return json.dumps(user_dict)\
    except:\
        pass\
    try:\
        return base64.b64decode(data[:-5][::-1])\
    except:\
        return ""' /app/ServiceConfig/__init__.py
