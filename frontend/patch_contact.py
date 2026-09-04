# coding=utf-8
import re
import codecs

with codecs.open('src/views/ContactView.vue', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('Contact Us', 'ติดต่อเรา')
content = content.replace('Have questions or need assistance? Our team is here to help.', 'มีคำถามหรือต้องการความช่วยเหลือ? ทีมงานของเราพร้อมให้บริการ')
content = content.replace('Send us a message', 'ส่งข้อความถึงเรา')
content = content.replace('Full Name', 'ชื่อ-นามสกุล')
content = content.replace('John Doe', 'สมชาย ใจดี')
content = content.replace('Email Address', 'อีเมล')
content = content.replace('john@example.com', 'somchai@example.com')
content = content.replace('Subject', 'หัวข้อ')
content = content.replace('How can we help?', 'ให้เราช่วยเหลือเรื่องใด?')
content = content.replace('Message', 'ข้อความ')
content = content.replace('Tell us more about your inquiry...', 'บอกรายละเอียดเพิ่มเติมเกี่ยวกับการสอบถามของคุณ...')
content = content.replace('Send Message', 'ส่งข้อความ')
content = content.replace('Sending...', 'กำลังส่ง...')
content = content.replace('Office Address', 'ที่อยู่สำนักงาน')
content = content.replace('เลขที่ 120 หมู่ 3 ชั้น 3 และ 5', 'สำนักงานคณะกรรมการดิจิทัลเพื่อเศรษฐกิจและสังคมแห่งชาติ (สดช.)<br>เลขที่ 120 หมู่ 3 ชั้น 3 และ 5')
content = content.replace('Direct Contact', 'ข้อมูลติดต่อโดยตรง')
content = content.replace('Frequently Asked Questions', 'คำถามที่พบบ่อย')
content = content.replace("How do I request access to restricted data?", 'ฉันจะขอเข้าถึงข้อมูลที่ถูกจำกัดได้อย่างไร?')
content = content.replace('You can apply for access by clicking the "Request Access" button on the dataset detail page. You will need to provide a justification for your research or project.', 'คุณสามารถสมัครขอเข้าถึงข้อมูลได้โดยคลิกปุ่ม "ขอสิทธิ์เข้าถึง" ในหน้ารายละเอียดชุดข้อมูล โดยคุณต้องระบุเหตุผลในการวิจัยหรือโครงการของคุณ')
content = content.replace('What are the API rate limits?', 'ข้อจำกัดในการเรียกใช้ API คืออะไร?')
content = content.replace('Standard API keys have a limit of 1,000 requests per hour. For higher limits, please contact our support team.', 'คีย์ API มาตรฐานมีข้อจำกัดในการเรียกใช้งาน 1,000 ครั้งต่อชั่วโมง หากต้องการขยายขีดจำกัด โปรดติดต่อทีมสนับสนุนของเรา')
content = content.replace('How can I contribute my own datasets?', 'ฉันจะนำชุดข้อมูลของตัวเองมาเผยแพร่ได้อย่างไร?')
content = content.replace('Agencies can register as data providers through the "Provider Portal". Once registered, you can upload and manage your datasets.', 'หน่วยงานสามารถลงทะเบียนเป็นผู้ให้บริการข้อมูลผ่าน "พอร์ทัลผู้ให้บริการ" เมื่อลงทะเบียนแล้ว คุณสามารถอัปโหลดและจัดการชุดข้อมูลของคุณได้')

with codecs.open('src/views/ContactView.vue', 'w', 'utf-8') as f:
    f.write(content)
