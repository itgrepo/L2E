import { NextResponse } from 'next/server';

export async function GET() {
  const datasets = {
    status: 'success',
    data: [
      {
        service_id: 1,
        dataset_id: 'POP-001',
        service_name: 'สถิติจำนวนประชากรแยกตามรายหน้า พ.ศ. 2566',
        organization: 'กรมการปกครอง',
        data_format: 'CSV,API,JSON',
        accessibility: 'Open Data',
        category: 'ข้อมูลประชากร',
        api_enabled: 1
      },
      {
        service_id: 2,
        dataset_id: 'REG-001',
        service_name: 'ข้อมูลทะเบียนราษฎร์และบ้านรายเขต (กรุงเทพฯ)',
        organization: 'กทม.',
        data_format: 'JSON',
        accessibility: 'Open Data',
        category: 'ข้อมูลประชากร'
      },
      {
        service_id: 3,
        dataset_id: 'HLT-001',
        service_name: 'ข้อมูลสถานพยาบาลและเตียงผู้ป่วย',
        organization: 'กระทรวงสาธารณสุข',
        data_format: 'CSV,API',
        accessibility: 'Open Data',
        category: 'สาธารณสุข'
      },
      {
        service_id: 4,
        dataset_id: 'SOC-001',
        service_name: 'สถิติการรับเงินเบี้ยยังชีพผู้สูงอายุ',
        organization: 'กรมส่งเสริมการปกครองท้องถิ่น',
        data_format: 'XLSX,API',
        accessibility: 'Restricted',
        category: 'สวัสดิการสังคมและสิทธิมนุษยชน'
      },
      {
        service_id: 5,
        dataset_id: 'EDU-001',
        service_name: 'รายชื่อโรงเรียนและจำนวนนักเรียน',
        organization: 'สพฐ.',
        data_format: 'CSV',
        accessibility: 'Open Data',
        category: 'การศึกษา'
      },
      {
        service_id: 6,
        dataset_id: 'ECN-001',
        service_name: 'ดัชนีความเชื่อมั่นผู้บริโภค',
        organization: 'กระทรวงพาณิชย์',
        data_format: 'API,JSON',
        accessibility: 'Open Data',
        category: 'เศรษฐกิจ'
      },
      {
        service_id: 7,
        dataset_id: 'HLT-002',
        service_name: 'สถิติผู้ป่วยนอกแยกตามกลุ่มโรค',
        organization: 'กรมการแพทย์',
        data_format: 'CSV,XLSX',
        accessibility: 'Open Data',
        category: 'สาธารณสุข'
      }
    ]
  };

  return NextResponse.json(datasets);
}
