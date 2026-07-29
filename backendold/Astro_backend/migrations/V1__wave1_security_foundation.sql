-- Update access_type to standard lowercase values
UPDATE service SET access_type = 'public' WHERE access_type IN ('Public', '');
UPDATE service SET access_type = 'internal' WHERE access_type = 'Confidential';
UPDATE service SET access_type = 'restricted' WHERE access_type = 'Restricted';

-- Add missing organization that exists in service table
INSERT INTO organization (org_name, create_at) 
SELECT 'สำนักงานปลัดกระทรวง พม. (OPS)', CURRENT_TIMESTAMP
WHERE NOT EXISTS (
    SELECT 1 FROM organization WHERE org_name = 'สำนักงานปลัดกระทรวง พม. (OPS)'
);
