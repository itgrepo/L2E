# Intelligist DataX - Installation Manual (AIS Cloud Deployment)

คู่มือฉบับนี้จัดทำขึ้นสำหรับทีมติดตั้งระบบ Intelligist DataX บนสภาพแวดล้อม AIS Cloud โดยใช้ **Interactive Launcher** เพื่อความสะดวกและรวดเร็ว

## 1. ความต้องการของระบบ (System Requirements)

เพื่อให้ระบบทำงานได้อย่างเสถียร แนะนำให้เตรียมทรัพยากรดังนี้:

| รายการ | ความต้องการขั้นต่ำ | แนะนำ (Recommended) |
| :--- | :--- | :--- |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **vCPU** | 2 Cores | 4 Cores |
| **RAM** | 4 GB | 8 GB |
| **Storage (SSD)** | 40 GB | 60 GB+ |
| **Network** | Public IP (Floating IP) | Public IP + Domain Name |

---

## 2. การเตรียมความพร้อมก่อนติดตั้ง (Pre-installation Checklist)

### 2.1 การเปิด Firewall (Security Groups)
กรุณาเปิด Port ต่อไปนี้บน AIS Cloud Console:
- **Port 22 (SSH)**: สำหรับผู้ดูแลระบบ
- **Port 80 / 443**: ช่องทางหลักสำหรับ Frontend
- **Port 3000 / 3001**: สำหรับการเชื่อมต่อ Backend และ UAT Portal (หากระบุตอนติดตั้ง)

### 2.2 การติดตั้งซอฟต์แวร์พื้นฐาน
ในเครื่องเซิร์ฟเวอร์ต้องติดตั้ง Docker หากยังไม่มี ให้รันคำสั่งดังนี้:
```bash
# ติดตั้ง Docker และ Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```
*(หมายเหตุ: อาจต้อง Logout และ Login ใหม่เพื่อให้สิทธิ์ Docker มีผล)*

---

## 3. ขั้นตอนการติดตั้งด้วย Interactive Launcher

เราได้เตรียมสคริปต์ `setup.sh` เพื่อช่วยให้การติดตั้งทำได้โดยไม่ต้องแก้ไขโค้ดเอง

### 3.1 การเตรียมไฟล์
ตรวจสอบว่ามีไฟล์เหล่านี้อยู่ในโฟลเดอร์โปรเจกต์:
- `setup.sh` (ตัวรันหลัก)
- `docker-compose.uat.yml` (Template โครงสร้างระบบ)
- `init_db_uat.sh` (สคริปต์สร้างฐานข้อมูล)
- `.env.example` (Template สำหรับค่า Environment)

### 3.2 เริ่มการติดตั้ง
รันคำสั่งต่อไปนี้:
```bash
chmod +x setup.sh
./setup.sh
```

### 3.3 การใส่ข้อมูล (Wizard Inputs)
โปรแกรมจะถามข้อมูลสำคัญ 4 ส่วน:
1.  **Network Config**: ใส่เลข IP ของเซิร์ฟเวอร์
2.  **Database Config**: ตั้งรหัสผ่าน Database (แนะนำให้ตั้งใหม่เพื่อความปลอดภัย)
3.  **SMTP Config**: ใส่ข้อมูลเมลสำหรับส่ง Notification (เช่น Gmail App Password)
4.  **Confirmation**: พิมพ์ `y` เพื่อเริ่มการ Build และ Run ทันที

---

## 4. การตรวจสอบหลังการติดตั้ง (Post-Installation)

เมื่อสคริปต์รันเสร็จสิ้น คุณสามารถตรวจสอบระบบได้ดังนี้:

### 4.1 ตรวจสอบสถานะ Container
```bash
docker-compose -f docker-compose.uat.yml ps
```
ทุกรายการควรขึ้นสถานะ `Up`

### 4.2 ข้อมูลการเข้าใช้งาน
- **Frontend URL**: `http://<YOUR_IP>:3001`
- **Backend API**: `http://<YOUR_IP>:3000`

### 4.3 ดู Logs ของระบบ
หากพบปัญหา ให้ดู Logs เพื่อวิเคราะห์:
```bash
docker-compose -f docker-compose.uat.yml logs -f
```

---

## 5. การแก้ไขปัญหาเบื้องต้น (Troubleshooting)

| ปัญหา | สาเหตุที่พบบ่อย | วิธีแก้ไข |
| :--- | :--- | :--- |
| เข้าเว็บไม่ได้ | Firewall ไม่ได้เปิด Port 3001 | เช็ค Security Group บน AIS Cloud |
| ส่งเมลไม่ได้ | App Password ของ Gmail ไม่ถูกต้อง | ตรวจสอบรหัสในไฟล์ .env และแก้ไขตามต้องการ |
| ฐานข้อมูลไม่ขึ้น | คอนเทนเนอร์ db ยังรันไม่เสร็จตอนรัน script | รัน `./init_db_uat.sh` ซ้ำอีกครั้ง |

> [!IMPORTANT]
> **ความปลอดภัย**: หลังจากติดตั้งเสร็จแล้ว ไฟล์ `.env` จะเก็บรหัสผ่านระบบไว้ในที่เดียว กรุณาจำกัดสิทธิ์การเข้าถึงไฟล์นี้เฉพาะผู้ดูแลระบบเท่านั้น
