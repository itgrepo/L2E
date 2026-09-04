# coding=utf-8
import codecs

with codecs.open('src/views/DatasetApprovalView.vue', 'r', 'utf-8') as f:
    content = f.read()

old_th = """<th>ผู้ใช้งาน</th>
              <th>ชุดข้อมูลที่ขอ</th>"""

new_th = """<th>ชื่อ-นามสกุลจริง</th>
              <th>อีเมลสังกัด</th>
              <th>ชื่อหน่วยงาน</th>
              <th>ชุดข้อมูลที่ขอ</th>"""

old_td = """<td>{{ req.username }}</td>
              <td>{{ req.service_name || req.service_id }}</td>"""

new_td = """<td>{{ req.firstname }} {{ req.lastname }}</td>
              <td>{{ req.email }}</td>
              <td>{{ req.organization || '-' }}</td>
              <td>{{ req.service_name || req.service_id }}</td>"""

content = content.replace(old_th, new_th).replace(old_td, new_td)

with codecs.open('src/views/DatasetApprovalView.vue', 'w', 'utf-8') as f:
    f.write(content)
