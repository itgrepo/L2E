## 📂 โครงสร้างโปรเจกต์ (Monorepo Structure)

```text
intelligist-datax/
├── package.json         # 🛠️ Root package (สำหรับรันทั้งหน้า-หลังพร้อมกัน)
├── frontend/           # 🧩 Vue.js Frontend
│   ├── src/
│   ├── components/      # ที่เก็บ Widget ทั้งหมด
│   └── .env             # ตั้งค่า API URL ที่นี่
└── backend/            # 🚀 Next.js Backend (Mock API)
    └── src/app/api/     # ที่เก็บ API Routes (/features, /steps)
```

---

## 🚀 วิธีเริ่มต้นใช้งาน (Getting Started)

1.  **ติดตั้ง Dependencies ครั้งแรก:**
    ```bash
    npm run install:all
    ```
2.  **รันทั้ง Frontend และ Backend พร้อมกัน:**
    ```bash
    npm run dev
    ```
    *   **Frontend:** จะรันอยู่ที่ `http://localhost:3001`
    *   **Backend:** จะรันอยู่ที่ `http://localhost:3000`


---

## 📝 วิธีแก้ไขเนื้อหา (Editing Content)

### 1. แก้ไขข้อความในรายการ (Arrays)
สำหรับส่วนที่มีรายการซ้ำๆ เช่น **Features** หรือ **Steps** คุณสามารถแก้ได้ง่ายๆ ที่ส่วน `<script setup>` ของไฟล์นั้นๆ:

*   **แก้ไข Feature:** ไปที่ `src/components/FeatureSection.vue`
*   **แก้ไขขั้นตอน (Steps):** ไปที่ `src/components/StepSection.vue`

หาตัวแปร `const features = [...]` หรือ `const steps = [...]` แล้วเปลี่ยนข้อความในนั้นได้เลย

### 2. แก้ไขหัวข้อ (Headlines)
สำหรับหัวข้อหลักของแต่ละส่วน ให้เปิดไฟล์ `.vue` ของส่วนนั้นแล้วแก้ในส่วน `<template>` ได้โดยตรง

---

## 🎨 การปรับแต่งดีไซน์ (Styling & Design)

### 1. เปลี่ยนสีหลัก (Global Theme)
หากต้องการเปลี่ยนสีเขียว หรือฟอนต์ ให้ไปที่ `src/style.css`:
```css
:root {
  --primary: #1d5d46;        /* แก้สีหลักตรงนี้ */
  --primary-hover: #154634;  /* สีตอนเอาเมาส์วาง */
  --bg-main: #f8fafc;        /* สีพื้นหลัง */
}
```

### 2. แก้ไขสไตล์เฉพาะส่วน (Scoped CSS)
ในแต่ละไฟล์ `.vue` จะมีส่วน `<style scoped>` อยู่ท้ายไฟล์ ซึ่งจะส่งผล **เฉพาะไฟล์นั้นๆ** เท่านั้น ทำให้แก้แล้วไม่ไปกระทบส่วนอื่น

---

## 🚀 วิธีเพิ่ม Widget ใหม่
1. สร้างไฟล์ใหม่ใน `src/components/YourNewWidget.vue`
2. ใส่ `template`, `script`, และ `style`
3. ไปที่ `src/App.vue` เพื่อนำเข้า (Import) และวางตำแหน่งที่ต้องการ:
   ```javascript
   import YourNewWidget from './components/YourNewWidget.vue';
   ```
   ```html
   <template>
     ...
     <YourNewWidget />
     ...
   </template>
   ```

---

## 🖥️ การแยกเครื่องรัน (Separate UAT Machines)

หากคุณต้องรัน Frontend และ Backend แยกเครื่องกัน (เช่น UAT Server 2 เครื่อง):

### 1. ตั้งค่า IP ของแต่ละเครื่อง
แก้ไขไฟล์ใน `frontend/`:
- **`.env.development`**: สำหรับรันในเครื่องตัวเอง (localhost)
- **`.env.uat`**: ใส่ IP ของเครื่อง Backend UAT ที่นี่

### 2. วิธี Build สำหรับแต่ละสภาพแวดล้อม
```bash
# สำหรับรันปกติ (Local)
npm run dev

# สำหรับ Build ไปลงเครื่อง UAT
cd frontend
npm run build:uat
```
เมื่อรัน `build:uat` ระบบจะดึงค่าจาก `.env.uat` ไปใส่ในไฟล์ที่ Build ออกมา (ในโฟลเดอร์ `dist/`) เพื่อให้ Frontend เชื่อมต่อกับ Backend ที่อยู่อีกเครื่องได้ถูกต้องครับ

---

## 🌐 การเชื่อมต่อกับ Backend (API Integration)

โปรเจกต์นี้ตั้งค่าให้เชื่อมต่อกับ **Next.js Backend** โดยใช้ `axios`

### 1. การตั้งค่า URL ของ Backend
แก้ไขที่ไฟล์ `.env` ในโฟลเดอร์ root:
```env
VITE_API_URL=http://localhost:3000/api
```

### 2. การเรียกใช้ API
เรามีตัวจัดการ API อยู่ที่ `src/services/api.js` ซึ่งคุณสามารถ import ไปใช้ในคอมโพเนนต์ต่างๆ ได้:

```javascript
import api from '../services/api';

// ตัวอย่างการเรียกใช้
const response = await api.get('/your-endpoint');
```

### 3. ส่วนประกอบที่เชื่อมต่อ API แล้ว
*   **FeatureSection.vue**: ดึงข้อมูลจาก `GET /features`
*   **StepSection.vue**: ดึงข้อมูลจาก `GET /steps`

*หมายเหตุ: หาก API ล่ม ระบบจะใช้ข้อมูลสำรอง (Fallback) เพื่อให้หน้าเว็บยังสวยงามอยู่*

---

*สร้างโดย Antigravity AI Code Assistant*
