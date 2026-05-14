import { NextResponse } from 'next/server';

export async function GET() {
  const statsData = {
    status: 'success',
    stats: [
      { label: 'Datasets Accessed', value: '156', trend: '+12%', color: '#e91e63', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2z' },
      { label: 'API Keys Active', value: '42', trend: '+5%', color: '#3b82f6', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
      { label: 'API Calls This Month', value: '2.4M', trend: '+18%', color: '#8b5cf6', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16' },
      { label: 'Downloads This Month', value: '850', trend: '+8%', color: '#ef4444', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4' }
    ],
    recentActivity: [
      { type: 'API', text: 'API call from Python script (IP: 192.168.1.45)', time: '2 minutes ago' },
      { type: 'Download', text: 'User downloaded "Health Stats 2023"', time: '1 hour ago' },
      { type: 'API', text: 'New API Key generated for Service L2E', time: '3 hours ago' },
      { type: 'Dataset', text: 'New dataset "Population Census" published', time: '5 hours ago' },
      { type: 'API', text: 'Authentication success for testadmin', time: '1 day ago' }
    ]
  };

  return NextResponse.json(statsData);
}
