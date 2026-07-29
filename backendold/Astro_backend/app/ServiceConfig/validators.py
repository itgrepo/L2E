def validate_dataset_masters(cursor, category_name, org_name, access_type):
    if access_type not in ['public', 'internal', 'restricted', 'pii']:
        return False, f"Invalid access_type: {access_type}"
    
    if category_name:
        cursor.execute("SELECT 1 FROM category WHERE category_name = %s", (category_name,))
        if not cursor.fetchone():
            return False, f"Category '{category_name}' not found."
            
    if org_name:
        cursor.execute("SELECT 1 FROM organization WHERE org_name = %s", (org_name,))
        if not cursor.fetchone():
            return False, f"Organization '{org_name}' not found."
            
    return True, ""
