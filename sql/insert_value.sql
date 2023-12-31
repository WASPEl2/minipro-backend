INSERT INTO menu_type (menu_type_name, store_id)
VALUES ('ประเภทเมนู 1', 1),
        ('ประเภทเมนู 2', 1),
        ('ประเภทเมนู 3', 1),

-- Inserting sample data into the customer table
INSERT INTO customer ( customer_username, customer_pwd, customer_phone, customer_mail)
VALUES
    ('john_doe', 'password123', '1234567890', 'john.doe@email.com'),
    ('jane_smith', 'securepass', '9876543210', 'jane.smith@email.com'),
    ('bob_jones', 'bobspassword', '5551234567', 'bob.jones@email.com');

INSERT INTO addon (addon_name, choices, store_id, areRequir)
VALUES
('Sweetness Level', '[{"name": "Very Sweet", "price": 5.0, "areSale": true}, {"name": "Moderately Sweet", "price": 3.0, "areSale": true}, {"name": "Not Sweet", "price": 0.0, "areSale": true}]', 1, true),
('Vegetable Option', '[{"name": "No Vegetables", "price": 0.0, "areSale": true}, {"name": "With Cilantro", "price": 2.0, "areSale": true}, {"name": "No Sprouts", "price": 1.0, "areSale": true}]', 1, true),
('Protein Choice', '[{"name": "Chicken", "price": 5.0, "areSale": true}, {"name": "Pork", "price": 5.0, "areSale": true}, {"name": "Fish", "price": 8.0, "areSale": true}, {"name": "Beef", "price": 7.0, "areSale": true}]', 1, true);


INSERT INTO menu (menu_id, menu_name, menu_price, store_id)
VALUES (1, 'Spaghetti Bolognese', 12.0, 1);

INSERT INTO menu (menu_id, menu_name, menu_price, store_id)
VALUES (2, 'Margherita Pizza', 10.0, 1);

INSERT INTO menu (menu_id, menu_name, menu_price, store_id)
VALUES (3, 'Chicken Stir-Fry', 15.0, 1);

INSERT INTO menu (menu_id, menu_name, menu_price, store_id)
VALUES (4, 'Vegetarian Salad', 8.0, 1);

INSERT INTO menu (menu_id, menu_name, menu_price, store_id)
VALUES (5, 'Beef Tacos', 14.0, 1);

-- Simulating menu data
INSERT INTO menu (menu_image, menu_name, menu_description, menu_price, menu_addon, menu_menutype, store_id)
VALUES
(null, 'Pad Thai', 'Stir-fried rice noodle dish', 10.0, '[1,2,3]', '[1]', 1),
(null, 'Tom Yum Soup', 'Hot and sour Thai soup', 8.0, '[2]', '[2]', 1);

INSERT INTO transfer_slip (transferslip_ref, transferslip_timestamp, transferslip_price, transferslip_sender, transferslip_receiver)
VALUES ('2023111399386992', '2023-11-13 10:00:00', 100.50, 'SenderName', 'ReceiverName');

INSERT INTO `order` ( customer_id, transferslip_ref, order_status, order_totalprice)
SELECT
    FLOOR(RAND() * 3) + 1, -- Random customer_id between 1 and 3 (adjust as needed)
    '2023111399386992',
    CASE
        WHEN RAND() < 0.2 THEN 'wait payment' -- 20% chance of 'wait payment'
        WHEN RAND() < 0.4 THEN 'pending' -- 20% chance of 'pending'
        WHEN RAND() < 0.6 THEN 'cooking' -- 20% chance of 'cooking'
        WHEN RAND() < 0.8 THEN 'waiting' -- 20% chance of 'waiting'
        ELSE 'complete' -- 20% chance of 'complete'
    END,
    ROUND(RAND() * 100 + 50, 2) -- Random order_totalprice between 50 and 150
FROM
    information_schema.tables
LIMIT 20;

INSERT INTO order_menu (order_id, menu_id, addon_id, choice_select, choice_price, menu_quantity, menu_status, menu_totalprice)
SELECT
    FLOOR(1 + RAND() * 100) as order_id,
    t1.n as menu_id,
    FLOOR(1 + RAND() * 3) as addon_id,
    FLOOR(1 + RAND() * 3) as choice_select,
    ROUND(RAND() * 10, 2) as choice_price,
    FLOOR(1 + RAND() * 3) as menu_quantity,
    CASE
        WHEN RAND() < 0.2 THEN 'wait payment'
        WHEN RAND() < 0.4 THEN 'pending'
        WHEN RAND() < 0.6 THEN 'cooking'
        WHEN RAND() < 0.8 THEN 'waiting'
        ELSE 'complete'
    END as menu_status,
    0 as menu_totalprice
FROM
    (SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t1,
    (SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t2,
    (SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t3
WHERE
    NOT EXISTS (
        SELECT 1
        FROM order_menu om
        WHERE om.order_id = FLOOR(1 + RAND() * 100)  -- Same as the generated order_id
          AND om.menu_id = t1.n  -- Same as the generated menu_id
    )
LIMIT 40;

UPDATE order_menu
SET menu_description = "อธิบายเพิ่มเติม"
WHERE order_id > 35;