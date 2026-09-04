filepath = 'frontend/nginx.conf'
with open(filepath, 'r') as f:
    content = f.read()

cache_rules = """
        # Prevent caching of index.html
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        }
        
        # Cache static assets but allow revalidation
        location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico)$ {
            expires 1y;
            add_header Cache-Control "public, max-age=31536000, immutable";
        }
"""
content = content.replace("try_files $uri $uri/ /index.html;", "try_files $uri $uri/ /index.html;\n" + cache_rules)

with open(filepath, 'w') as f:
    f.write(content)
