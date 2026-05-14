import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const { username, password } = body;

    // Mock Login Logic
    if (username === 'testadmin' && password === 'password123') {
      return NextResponse.json({
        status: 'success',
        data: {
          user_id: '809',
          username: 'testadmin',
          firstname: 'System',
          lastname: 'Admin',
          role: 'admin',
          apikey: 'ms_society_live_key_9988776655'
        }
      });
    }
    
    if (username === 'developer' && password === 'dev1234') {
      return NextResponse.json({
        status: 'success',
        data: {
          user_id: '12',
          username: 'developer',
          firstname: 'Developer',
          lastname: 'System',
          role: 'admin',
          apikey: 'dev_key_12345'
        }
      });
    }

    return NextResponse.json({
      status: 'error',
      message: 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
    }, { status: 401 });

  } catch (e) {
    return NextResponse.json({ status: 'error', message: 'Internal Server Error' }, { status: 500 });
  }
}
