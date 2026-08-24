-- Clear old permissions
DELETE FROM menu_permission;

-- Insert new permissions logic
-- R1 (1): None, or just Catalog
-- R2 (2): Dashboard, Catalog
-- R3 (3): Dashboard, Catalog, API Management, API Monitor, Dataset Approval, Dataset Management, Analytics
-- R4 (4): All
-- R5 (5): Dashboard, Catalog, API Management

-- Insert for R1
INSERT INTO menu_permission (previlage_id, menu_name_id, value) SELECT 1, menu_name_id, 'No' FROM menu_name;

-- Insert for R2
INSERT INTO menu_permission (previlage_id, menu_name_id, value) SELECT 2, menu_name_id, 'No' FROM menu_name;
UPDATE menu_permission SET value = 'Yes' WHERE previlage_id = 2 AND menu_name_id IN (1, 2, 11, 12, 18, 19);

-- Insert for R3
INSERT INTO menu_permission (previlage_id, menu_name_id, value) SELECT 3, menu_name_id, 'No' FROM menu_name;
UPDATE menu_permission SET value = 'Yes' WHERE previlage_id = 3 AND menu_name_id IN (1, 2, 3, 4, 5, 6, 9, 11, 12, 13, 14, 18, 19, 20, 21);

-- Insert for R4
INSERT INTO menu_permission (previlage_id, menu_name_id, value) SELECT 4, menu_name_id, 'Yes' FROM menu_name;

-- Insert for R5
INSERT INTO menu_permission (previlage_id, menu_name_id, value) SELECT 5, menu_name_id, 'No' FROM menu_name;
UPDATE menu_permission SET value = 'Yes' WHERE previlage_id = 5 AND menu_name_id IN (1, 2, 3, 11, 12, 13, 18, 19, 20);

