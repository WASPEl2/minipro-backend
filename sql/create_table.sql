DROP TABLE menu;
DROP TABLE menu_type;
DROP TABLE addon;
DROP TABLE openTime;
DROP TABLE store;
DROP TABLE customer;

CREATE TABLE customer
(
    customer_id INT NOT NULL,
    customer_name VARCHAR(40) NOT NULL,
    customer_pwd VARCHAR(40) NOT NULL,
    PRIMARY KEY (customer_id)
);

CREATE TABLE store
(
    store_id INT NOT NULL AUTO_INCREMENT,
    store_name VARCHAR(40) NOT NULL,
    store_username VARCHAR(120) NOT NULL,
    store_number VARCHAR(10) NOT NULL,
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

CREATE TABLE addon_category
(
    addon_category_id INT NOT NULL AUTO_INCREMENT,
    addon_category_name VARCHAR(60) NOT NULL,
    store_id INT NOT NULL,
    areRequir BOOLEAN NOT NULL,
    areNulti BOOLEAN NOT NULL,
    PRIMARY KEY (addon_category_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE TABLE addon
(
    addon_id INT NOT NULL AUTO_INCREMENT,
    addon_name VARCHAR(60) NOT NULL,
    addon_category_id VARCHAR(60) NOT NULL,
    addon_price VARCHAR(10) NOT NULL,
    PRIMARY KEY (addon_id),
    FOREIGN KEY (addon_category_id) REFERENCES addon_category(addon_category_id)
);

CREATE TABLE menu_type
(
    menu_type_id INT NOT NULL AUTO_INCREMENT,
    menu_type_name VARCHAR(60) NOT NULL,
    menu_type_priority int,
    store_id INT NOT NULL,
    PRIMARY KEY (menu_type_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE TABLE menu
(
    menu_id INT NOT NULL AUTO_INCREMENT,
    menu_name VARCHAR(60) NOT NULL,
    menu_price VARCHAR(10) NOT NULL,
    menu_type_id INT,
    store_id INT NOT NULL,
    addon_id INT,
    PRIMARY KEY (menu_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id),
    FOREIGN KEY (addon_id) REFERENCES addon(addon_id),
    FOREIGN KEY (menu_type_id) REFERENCES menu_type(menu_type_id)
);
