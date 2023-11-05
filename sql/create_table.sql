DROP TABLE menu;
DROP TABLE addon;
DROP TABLE store;
DROP TABLE rate;
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
    store_owner VARCHAR(120) NOT NULL,
    store_number VARCHAR(10) NOT NULL,
    store_pwd VARCHAR(40) NOT NULL,
    store_type VARCHAR(40) NOT NULL,
    store_locate VARCHAR(40) NOT NULL,
    store_image LONGBLOB,
    rate_show INT,
    PRIMARY KEY (store_id)
);

CREATE TABLE rate
(
    rate_id INT NOT NULL AUTO_INCREMENT,
    rate_show INT NOT NULL,
    rate_count INT NOT NULL,
    store_id INT NOT NULL,
    PRIMARY KEY (rate_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE TABLE addon
(
    addon_id INT NOT NULL AUTO_INCREMENT,
    addon_name VARCHAR(60) NOT NULL,
    addon_price VARCHAR(10) NOT NULL,
    store_id INT NOT NULL,
    PRIMARY KEY (addon_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);

CREATE TABLE menu
(
    menu_id INT NOT NULL AUTO_INCREMENT,
    menu_name VARCHAR(60) NOT NULL,
    menu_price VARCHAR(10) NOT NULL,

    store_id INT NOT NULL,
    addon_id INT,
    PRIMARY KEY (menu_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id),
    FOREIGN KEY (addon_id) REFERENCES addon(addon_id)
);
