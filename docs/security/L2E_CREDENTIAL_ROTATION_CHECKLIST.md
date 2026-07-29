# L2E CREDENTIAL ROTATION CHECKLIST

⚠️ **คำเตือนความปลอดภัย**: Credential ที่เคยปรากฏใน Script, Workspace หรือ Chat ต้องถูก Rotate โดยเจ้าของระบบก่อนขึ้น Production

## รายการที่ต้องดำเนินการ

- [ ] **เปลี่ยน Password ของ Administrator**: ตรวจสอบและเปลี่ยนรหัสผ่านของ Admin ที่เคยถูก Hardcode ไว้ในระบบหรือสคริปต์
- [ ] **สร้าง SSH Key Pair ใหม่**: สร้าง Key Pair ใหม่สำหรับเข้าถึง Server UAT/Production
- [ ] **เพิ่ม Public Key ใหม่ใน Server**: นำ Public Key ใหม่ไปใส่ใน `~/.ssh/authorized_keys` ของ Server
- [ ] **ทดสอบ Key ใหม่**: ยืนยันว่าสามารถ SSH เข้า Server ด้วย Key ใหม่ได้สำเร็จ
- [ ] **ถอน Public Key ของ `ubuntuL2E.key` เดิม**: ลบ Key เก่าออกจาก `authorized_keys` ทันทีหลังทดสอบ Key ใหม่ผ่าน
- [ ] **Rotate DB Test Credentials**: หากมี Database User ที่ใช้สำหรับ Test ต้องเปลี่ยนรหัสผ่านใหม่
- [ ] **Rotate Test API Keys**: เปลี่ยน API Keys หรือ Tokens ชั่วคราวทั้งหมดที่เคยใช้ในระหว่างการพัฒนา
- [ ] **ตรวจ Server Access Logs**: ตรวจสอบว่าไม่มีการเข้าถึงระบบที่ผิดปกติในช่วงที่มีการรั่วไหลของ Credential
- [ ] **ตรวจ Git History**: ดำเนินการล้างประวัติ Git (เช่น ใช้ BFG Repo-Cleaner) หากพบว่าเคยมีการ Commit Secret ลงใน Repository หลัก

*หมายเหตุ: ในรอบ Wave 0 นี้ ไม่มีการ Rotate หรือแก้ไข `authorized_keys` โดยอัตโนมัติ เนื่องจากเป็นการเปลี่ยนสิทธิ์ Server Access ที่ผู้ดูแลระบบต้องดำเนินการด้วยตนเอง*
