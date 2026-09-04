# coding=utf-8
import codecs

with codecs.open('src/views/UserManagementView.vue', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("showAlert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status), 'error');", "alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));")
content = content.replace("showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');", "alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');")

with codecs.open('src/views/UserManagementView.vue', 'w', 'utf-8') as f:
    f.write(content)
