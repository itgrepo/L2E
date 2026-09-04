import re

filepath = "frontend/src/views/ContactView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Email: and Phone: with SVG
email_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline; vertical-align:text-bottom; margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>'
phone_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline; vertical-align:text-bottom; margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>'

content = content.replace('<strong>Email:</strong>', f'<strong>{email_svg} Email:</strong>')
content = content.replace('<strong>Phone:</strong>', f'<strong>{phone_svg} Phone:</strong>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched ContactView")
