import { NextResponse } from 'next/server';

export async function POST() {
  return NextResponse.json({
    status: 'success',
    data: [
      { user_id: '809', username: 'testadmin', firstname: 'System', lastname: 'Admin' },
      { user_id: '101', username: 'test_new_001', firstname: 'test_new', lastname: 'test1' },
      { user_id: '102', username: 'analyst_01', firstname: 'Somsak', lastname: 'Data' }
    ]
  });
}
