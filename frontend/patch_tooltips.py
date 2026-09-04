# coding=utf-8
import codecs

with codecs.open('src/views/DatasetDetailView.vue', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'toggleFavorite(selectedDataset)' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="เพิ่ม/ลบ ชุดข้อมูลนี้ในรายการโปรดของคุณ">')
    elif 'activeTab = \'api\'' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดูเอกสารและการเชื่อมต่อ API">')
    elif 'activeTab = \'visual\'' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดูแดชบอร์ดสรุปผลข้อมูล">')
    elif 'btn-download csv' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดาวน์โหลดไฟล์ในรูปแบบ CSV">')
    elif 'btn-download xls' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดาวน์โหลดไฟล์ในรูปแบบ Excel">')
    elif 'ดาวน์โหลดพจนานุกรมข้อมูล' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดาวน์โหลดพจนานุกรมอธิบายโครงสร้างข้อมูล">')
    elif 'ดาวน์โหลดไฟล์แนบ (API File)' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดาวน์โหลดไฟล์เอกสารแนบต้นฉบับ">')
    elif 'ดาวน์โหลดชุดข้อมูลสุ่ม' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ดาวน์โหลดข้อมูลตัวอย่างสำหรับทดสอบ">')
    elif 'submitPermissionRequest' in line and '<button' in line and 'title=' not in line:
        lines[i] = line.replace('>', ' title="ส่งคำขอเพื่อให้ผู้ดูแลระบบอนุมัติสิทธิ์เข้าถึง">')

with codecs.open('src/views/DatasetDetailView.vue', 'w', 'utf-8') as f:
    f.writelines(lines)
