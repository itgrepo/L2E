USE datax_db_3003;
UPDATE service SET tags = CONCAT(IFNULL(tags, ''), ',job,l2e') WHERE service_id IN (1, 3, 21);
SELECT service_name, tags FROM service;
