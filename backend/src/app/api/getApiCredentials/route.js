import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log('Fetching API Credentials for:', body);
    
    return NextResponse.json({
      status: 'success',
      data: [
        {
          key_id: 1,
          username: 'test_new_001',
          full_name: 'test_new test1',
          apikey: 'ms_society_live_key_9988776655',
          status: 'Active',
          created_at: '2026-04-16',
          expired_at: '2026-04-30'
        }
      ]
    });
  } catch (e) {
    return NextResponse.json({ status: 'error', message: e.message }, { status: 400 });
  }
}
