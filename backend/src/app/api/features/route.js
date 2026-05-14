import { NextResponse } from 'next/server';

export async function GET() {
  const features = [
    { id: 1, title: 'ค้นหาชุดข้อมูล (From Next.js)', subtitle: 'ค้นหาข้อมูลที่คุณต้องการด้วยระบบที่ง่าย รวดเร็ว พร้อม metadata' },
    { id: 2, title: 'API Management', subtitle: 'จัดการ API Keys, ตั้งค่า Rate Limit และ Monitior การใช้งาน API ได้' },
    { id: 3, title: 'Data Integration', subtitle: 'เชื่อมต่อและบูรณาการข้อมูลผ่านระบบ ETL Pipeline พร้อม Validation & Transformation' },
    { id: 4, title: 'Usage Analytics', subtitle: 'ติดตามการใช้งาน API, ติดตามการดาวน์โหลด และ User Activity' },
    { id: 5, title: 'Data Governance', subtitle: 'จัดการนโยบายข้อมูล, สิทธิ์การเข้าถึงแบบ RBAC/ABAC และ Audit Trail' },
    { id: 6, title: 'Export & Download', subtitle: 'ดาวน์โหลดข้อมูลในรูปแบบ CSV, XLS หรือเชื่อมต่อผ่าน API ตามคุณต้องการ' }
  ];

  return NextResponse.json(features);
}
