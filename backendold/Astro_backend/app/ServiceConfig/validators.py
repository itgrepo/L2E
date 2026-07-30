def validate_dataset_masters(cursor, category_name, org_name, access_type, l2e_group_id=None, source_system_id=None, dataset_id=None):
    if access_type and access_type not in ['public', 'internal', 'restricted', 'pii']:
        return False, f"Invalid access_type: {access_type}"
    
    if category_name:
        cursor.execute("SELECT 1 FROM category WHERE category_name = %s", (category_name,))
        if not cursor.fetchone():
            return False, f"Category '{category_name}' not found."
            
    if org_name:
        cursor.execute("SELECT 1 FROM organization WHERE org_name = %s", (org_name,))
        if not cursor.fetchone():
            return False, f"Organization '{org_name}' not found."

    if l2e_group_id:
        cursor.execute("SELECT prefix FROM l2e_dataset_group WHERE id = %s AND active = 1", (l2e_group_id,))
        group_row = cursor.fetchone()
        if not group_row:
            return False, f"L2E Dataset Group ID '{l2e_group_id}' not found or inactive."
        
        prefix = group_row[0]
        if dataset_id and not dataset_id.startswith(prefix):
            return False, f"Dataset ID '{dataset_id}' must start with prefix '{prefix}' for this group."

    if source_system_id:
        cursor.execute("SELECT 1 FROM source_system WHERE id = %s AND active = 1", (source_system_id,))
        if not cursor.fetchone():
            return False, f"Source System ID '{source_system_id}' not found or inactive."

    return True, ""
