import { NextResponse } from 'next/server';

export async function GET() {
  const chartData = {
    status: 'success',
    data: [
      { date: '2026-04-22', count: 45 },
      { date: '2026-04-23', count: 52 },
      { date: '2026-04-24', count: 38 },
      { date: '2026-04-25', count: 65 },
      { date: '2026-04-26', count: 82 },
      { date: '2026-04-27', count: 91 },
      { date: '2026-04-28', count: 75 }
    ]
  };

  return NextResponse.json(chartData);
}
