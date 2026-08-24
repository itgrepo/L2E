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
        cursor.execute("SELECT 1 FROM group_user WHERE group_id = %s", (l2e_group_id,))
        if not cursor.fetchone():
            return False, f"Group ID '{l2e_group_id}' not found in group_user."

    if source_system_id:
        cursor.execute("SELECT 1 FROM source_system WHERE id = %s AND active = 1", (source_system_id,))
        if not cursor.fetchone():
            return False, f"Source System ID '{source_system_id}' not found or inactive."

    return True, ""
