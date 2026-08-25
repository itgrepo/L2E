# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

## ล่าสุด (อัปเดตสถิติหน้าแรก)
- **Frontend (`HeroSection.vue`)**: ปรับปรุงให้หน้า Landing Page (Hero Section) ดึงข้อมูลสถิติจริงจาก Backend มาแสดงผล แทนการใช้ตัวเลขแบบ Hardcode (เช่น จำนวนชุดข้อมูล, จำนวนหน่วยงานเครือข่าย, และ API Calls/เดือน)
- **Backend (`bigdataservice.py`)**: ปรับปรุง API `/dashboard/stats` ให้ส่งข้อมูล `hero_stats` (นับจำนวนหน่วยงานจากตาราง `organization`, นับจำนวนชุดข้อมูลที่ Active, และนับจำนวน API Calls จาก Log) เพื่อให้ Frontend นำไปแสดงผล
