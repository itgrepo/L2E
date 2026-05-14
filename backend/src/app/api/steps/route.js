import { NextResponse } from 'next/server';

export async function GET() {
  const steps = [
    { number: 1, title: 'สมัครสมาชิก (API)', desc: 'ลงทะเบียนด้วยอีเมลหน่วยงาน หรือเข้าสู่ระบบผ่าน SSO' },
    { number: 2, title: 'ค้นหาข้อมูล (API)', desc: 'เรียกดูชุดข้อมูลจาก Catalog หรือค้นหาด้วย Keyword' },
    { number: 3, title: 'ขอสิทธิ์เข้าถึง (API)', desc: 'ยื่นคำร้องเข้าถึงข้อมูลระดับ Field ที่ต้องการ' },
    { number: 4, title: 'ใช้งานข้อมูล (API)', desc: 'ดาวน์โหลดหรือเชื่อมต่อนำ API เพื่อนำไปใช้งาน' }
  ];

  return NextResponse.json(steps);
}
