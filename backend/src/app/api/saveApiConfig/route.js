import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    console.log('Received API Config:', body);
    
    return NextResponse.json({
      status: 'success',
      message: 'API configuration saved successfully'
    });
  } catch (e) {
    return NextResponse.json({ status: 'error', message: e.message }, { status: 400 });
  }
}
