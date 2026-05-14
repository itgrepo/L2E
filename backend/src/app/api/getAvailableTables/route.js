import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const dbName = body.db_name || 'default';
    
    const tablesByDb = {
      'psu_backend': [
        { name: 'export_metadata', type: 'table' },
        { name: 'service_config', type: 'table' },
        { name: 'user_logs', type: 'table' }
      ],
      'db_social_welfare': [
        { name: 'tb_elderly_allowance', type: 'table' },
        { name: 'tb_disability_support', type: 'table' },
        { name: 'vw_poverty_index_2023', type: 'view' }
      ],
      'db_population_stats': [
        { name: 'tb_birth_records', type: 'table' },
        { name: 'tb_migration_flow', type: 'table' },
        { name: 'vw_population_density', type: 'view' }
      ],
      'db_health_monitoring': [
        { name: 'tb_hospital_beds', type: 'table' },
        { name: 'tb_vaccination_log', type: 'table' }
      ]
    };

    return NextResponse.json({
      status: 'success',
      data: tablesByDb[dbName] || [
        { name: 'tb_generic_data_1', type: 'table' },
        { name: 'tb_generic_data_2', type: 'table' }
      ]
    });
  } catch (e) {
    return NextResponse.json({ status: 'error', message: e.message }, { status: 400 });
  }
}
