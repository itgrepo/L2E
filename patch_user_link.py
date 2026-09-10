import codecs

path = 'frontend/src/views/UserManagementView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = "submitData.password = encodePassword(submitData.password);"
injection = """submitData.password = encodePassword(submitData.password);
        submitData.link = window.location.origin;"""
content = content.replace(target, injection)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
