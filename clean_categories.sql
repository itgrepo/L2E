USE datax_db_3003;
DELETE FROM category WHERE category_name LIKE '%{%' OR category_name LIKE '%\'%';
DELETE FROM sub_category WHERE sub_category_name LIKE '%{%' OR sub_category_name LIKE '%\'%';
