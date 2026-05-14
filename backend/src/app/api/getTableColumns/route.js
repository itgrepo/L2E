import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const body = await request.json();
    const tableName = body.table_name || 'default';
    
    const columnsByTable = {
      'export_metadata': [
        { name: 'export_metadata_id', type: 'int' },
        { name: 'export_metadata_name', type: 'text' },
        { name: 'source_id', type: 'varchar' },
        { name: 'category_id', type: 'int' },
        { name: 'sub_category_id', type: 'int' },
        { name: 'file_name', type: 'text' },
        { name: 'created_at', type: 'datetime' }
      ],
      'tb_elderly_allowance': [
        { name: 'id', type: 'int' },
        { name: 'citizen_id', type: 'varchar(13)' },
        { name: 'first_name', type: 'varchar(100)' },
        { name: 'last_name', type: 'varchar(100)' },
        { name: 'age', type: 'int' },
        { name: 'province_code', type: 'varchar(2)' },
        { name: 'payment_status', type: 'varchar(20)' },
        { name: 'last_updated', type: 'timestamp' }
      ],
      'tb_birth_records': [
        { name: 'record_id', type: 'int' },
        { name: 'birth_date', type: 'date' },
        { name: 'gender', type: 'char(1)' },
        { name: 'weight_kg', type: 'decimal(5,2)' },
        { name: 'hospital_id', type: 'int' }
      ]
    };

    return NextResponse.json({
      status: 'success',
      data: columnsByTable[tableName] || [
        { name: 'id', type: 'int' },
        { name: 'data_value', type: 'text' },
        { name: 'created_at', type: 'datetime' }
      ]
    });
  } catch (e) {
    return NextResponse.json({ status: 'error', message: e.message }, { status: 400 });
  }
}
