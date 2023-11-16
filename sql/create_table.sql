DROP TABLE order_menu;
DROP TABLE `order`;
DROP TABLE transfer_slip;
DROP TABLE customer;
DROP TABLE menu_addon;
DROP TABLE menu_menutype;
DROP TABLE menu;
DROP TABLE menu_type;
DROP TABLE addon;
DROP TABLE openTime;
DROP TABLE store;

CREATE TABLE store
(
    store_id INT NOT NULL AUTO_INCREMENT,
    store_name VARCHAR(40) NOT NULL,
    store_username VARCHAR(120) NOT NULL UNIQUE,
    store_number VARCHAR(10) NOT NULL UNIQUE,
    store_pwd VARCHAR(40) NOT NULL,
    store_type VARCHAR(40) NOT NULL,
    store_locate VARCHAR(40) NOT NULL,
    store_image LONGBLOB NOT NULL,
    store_qr_code LONGBLOB NOT NULL,
    rate_show INT DEFAULT 0,
    rate_count INT DEFAULT 0,
    PRIMARY KEY (store_id)
);
CREATE TABLE openTime
(
    store_id INT NOT NULL ,
    day VARCHAR(20) NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    PRIMARY KEY (store_id, day),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);
CREATE TABLE addon
(
    addon_id INT NOT NULL AUTO_INCREMENT,
    addon_name VARCHAR(60) NOT NULL,
    addon_priority TINYINT UNSIGNED NOT NULL DEFAULT 0,
    store_id INT NOT NULL,
    areRequir BOOLEAN NOT NULL,
    choices JSON,
    PRIMARY KEY (addon_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);
CREATE TABLE menu_type
(
    menu_type_id INT NOT NULL AUTO_INCREMENT,
    menu_type_name VARCHAR(60) NOT NULL,
    menu_type_priority TINYINT UNSIGNED NOT NULL DEFAULT 0,
    store_id INT NOT NULL,
    PRIMARY KEY (menu_type_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);
CREATE TABLE menu
(
    menu_id INT NOT NULL AUTO_INCREMENT,
    menu_image LONGBLOB,
    menu_name VARCHAR(60) NOT NULL,
    menu_description VARCHAR(60),
    menu_price VARCHAR(10) NOT NULL,
    menu_addon JSON,
    menu_menutype JSON,
    store_id INT NOT NULL,
    PRIMARY KEY (menu_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);
CREATE TABLE menu_menutype
(
    menu_id INT NOT NULL,
    menu_type_id INT NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    FOREIGN KEY (menu_type_id) REFERENCES menu_type(menu_type_id)
);
CREATE TABLE menu_addon
(
    menu_id INT NOT NULL,
    addon_id INT NOT NULL,
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    FOREIGN KEY (addon_id) REFERENCES addon(addon_id)
);
CREATE TABLE customer
(
    customer_id INT NOT NULL AUTO_INCREMENT,
    customer_username VARCHAR(20) NOT NULL UNIQUE,
    customer_pwd VARCHAR(20) NOT NULL,
    customer_phone VARCHAR(10) NOT NULL UNIQUE,
    customer_mail VARCHAR(40) NOT NULL,
    PRIMARY KEY (customer_id)
);
CREATE TABLE transfer_slip
(   
    transferslip_ref VARCHAR(20) NOT NULL, -- dont forget to input ex. '2023111399386992'
    transferslip_image LONGBLOB NOT NULL,
    transferslip_timestamp TIMESTAMP NOT NULL,
    transferslip_price FLOAT NOT NULL,
    transferslip_sender VARCHAR(80) NOT NULL,
    transferslip_receiver VARCHAR(80) NOT NULL,
    PRIMARY KEY (transferslip_ref)
);
CREATE TABLE `order`
(
    order_id INT NOT NULL AUTO_INCREMENT,
    order_rate FLOAT ,
    order_status VARCHAR(20) NOT NULL, -- "wait paymeny" "pending" "cooking" "waiting" "complete"
    order_totalprice FLOAT NOT NULL,
    customer_id INT NOT NULL,
    transferslip_ref VARCHAR(20) NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (transferslip_ref) REFERENCES transfer_slip(transferslip_ref)
);
CREATE TABLE order_menu
(
    order_id INT NOT NULL,
    menu_id INT NOT NULL, -- one order can be many menu now i have menu id 1 - 5
    addon_id INT,
    choice_select INT, -- one addon can choose only one choice
    choice_price FLOAT, -- if have choice_select must have this
    menu_quantity INT NOT NULL,
    menu_description VARCHAR(200),
    menu_status VARCHAR(20) NOT NULL,
    menu_totalprice FLOAT,  -- calculate by menu price + all addon one menu can have meny addon
    FOREIGN KEY (order_id) REFERENCES `order`(order_id),
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    FOREIGN KEY (addon_id) REFERENCES addon(addon_id),
    CHECK (
        (choice_select IS NULL AND choice_price IS NULL) OR
        (choice_select IS NOT NULL AND choice_price IS NOT NULL)
    )
);


