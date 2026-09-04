# coding=utf-8
import re
import codecs

with codecs.open('src/views/AboutView.vue', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('About DataX Portal', 'เกี่ยวกับ DataX Portal')
content = content.replace('The central hub for BDE data exchange and API management.', 'ศูนย์กลางสำหรับการแลกเปลี่ยนข้อมูลและการจัดการ API')
content = content.replace('Our Mission', 'พันธกิจของเรา')
content = content.replace('DataX Portal (BDE Data Exchange & API Management Platform) is designed to streamline the way government agencies share, discover, and utilize data. Our mission is to create a seamless, secure, and standardized ecosystem that empowers developers and policy-makers with high-quality data.', 'DataX Portal (แพลตฟอร์มการแลกเปลี่ยนข้อมูลและการจัดการ API) ถูกออกแบบมาเพื่อเพิ่มประสิทธิภาพในการแบ่งปัน ค้นพบ และใช้ประโยชน์จากข้อมูลของหน่วยงานภาครัฐ พันธกิจของเราคือการสร้างระบบนิเวศที่ไร้รอยต่อ ปลอดภัย และมีมาตรฐาน เพื่อเสริมสร้างขีดความสามารถให้นักพัฒนาและผู้กำหนดนโยบายด้วยข้อมูลที่มีคุณภาพสูง')
content = content.replace('How it works', 'กระบวนการทำงาน')
content = content.replace('Discover', 'ค้นพบ')
content = content.replace('Easily find the data you need through our powerful search and smart categorization system.', 'ค้นหาข้อมูลที่คุณต้องการได้อย่างง่ายดายผ่านระบบค้นหาและจัดหมวดหมู่อัจฉริยะของเรา')
content = content.replace('Connect', 'เชื่อมต่อ')
content = content.replace('Get instant access via standardized APIs with complete documentation and code samples.', 'เข้าถึงข้อมูลได้ทันทีผ่าน API ที่ได้มาตรฐาน พร้อมเอกสารประกอบและตัวอย่างโค้ดที่สมบูรณ์')
content = content.replace('Secure', 'ปลอดภัย')
content = content.replace('Industry-standard authentication and auditing ensure that data is only accessed by authorized parties.', 'ระบบการยืนยันตัวตนและการตรวจสอบตามมาตรฐานอุตสาหกรรม เพื่อให้มั่นใจว่าข้อมูลเข้าถึงได้เฉพาะผู้ที่ได้รับอนุญาตเท่านั้น')
content = content.replace('Analyze', 'วิเคราะห์')
content = content.replace('Monitor your data usage and gain insights through comprehensive analytics dashboards.', 'ติดตามการใช้งานข้อมูลของคุณและรับข้อมูลเชิงลึกผ่านหน้าจอแดชบอร์ดการวิเคราะห์ที่ครอบคลุม')

with codecs.open('src/views/AboutView.vue', 'w', 'utf-8') as f:
    f.write(content)
