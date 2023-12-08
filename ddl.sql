-- Disabling commits and foreign key checks
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;

-- ------------------------------------------
-- DROP ALL TABLES BEFORE CREATING THEM.
-- ------------------------------------------
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS cultures;
DROP TABLE IF EXISTS breadProducts;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS soldProducts;
DROP TABLE IF EXISTS allergens;
DROP TABLE IF EXISTS allergensProducts;

-- ------------------------------------------
-- TABLE: customers
-- ------------------------------------------
CREATE TABLE customers (
  customerID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(45) NOT NULL,
  email VARCHAR(45) NOT NULL,
  phoneNumber VARCHAR(45) NOT NULL,
  streetAddress VARCHAR(45) NOT NULL,
  city VARCHAR(45) NOT NULL,
  state VARCHAR(45) NOT NULL,
  zipCode VARCHAR(45) NOT NULL,
  PRIMARY KEY (customerID)
);

-- -----------------------------------------------------
-- TABLE: cultures
-- -----------------------------------------------------
CREATE TABLE cultures (
  cultureID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(45) NOT NULL,
  PRIMARY KEY (cultureID)
);

-- -----------------------------------------------------
-- Table: breadProducts
-- -----------------------------------------------------
CREATE TABLE breadProducts (
  productID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(45) NOT NULL,
  unitPrice DECIMAL(10,2) NOT NULL,
  count INT NOT NULL,
  netWeight DECIMAL(10,2) NOT NULL,
  cultureID INT NOT NULL,
  PRIMARY KEY (productID),
  FOREIGN KEY (cultureID) references cultures(cultureID) ON DELETE RESTRICT
);

-- -----------------------------------------------------
-- TABLE: sales
-- -----------------------------------------------------
CREATE TABLE sales (
  saleID INT NOT NULL AUTO_INCREMENT,
  customerID INT NOT NULL,
  saleTotal DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (saleID),
  FOREIGN KEY (customerID) references customers(customerID) ON DELETE RESTRICT
);

-- -----------------------------------------------------
-- TABLE: soldProducts
-- -----------------------------------------------------
CREATE TABLE soldProducts (
  soldProductID INT NOT NULL AUTO_INCREMENT,
  saleID INT NOT NULL,
  productID INT NOT NULL,
  qtySold INT NOT NULL,
  lineTotal DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (soldProductID),
  FOREIGN KEY (saleID) references sales(saleID) ON DELETE CASCADE,
  FOREIGN KEY (productID) references breadProducts(productID) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- TABLE: allergens
-- -----------------------------------------------------
CREATE TABLE allergens (
  allergenID INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(45) NOT NULL,
  PRIMARY KEY (allergenID)
);

-- -----------------------------------------------------
-- TABLE: allergensProducts
-- -----------------------------------------------------
CREATE TABLE allergensProducts (
  allergensProductID INT NOT NULL AUTO_INCREMENT,
  productID INT NULL,
  allergenID INT NULL,
  PRIMARY KEY (allergensProductID),
  FOREIGN KEY (productID) references breadProducts(productID) ON DELETE CASCADE,
  FOREIGN KEY (allergenID) references allergens(allergenID) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- DATA: customers
-- -----------------------------------------------------
INSERT INTO customers (name, email, phoneNumber, streetAddress, city, state, zipCode) 
VALUES 
('Jalen Hurts', 'hurtsdonut@yahoo.com', '123-2342-2342', '322 Zimmerman Lane', 'Philadelphia', 'Pennsylvania', '90071'),
('Homer Simpson', 'ilikedonuts@springfield.com', '213-508-2677', '3165 Sycamore Road', ' Blodgett ', 'Oregon ', '97326'),
('John Johnson', 'pinkpanther@yahoo.com', '541-438-3638', ' 1311 Libby Street ', 'Gardena ', 'California ', '90247'),
('Jonah Cliffe', 'supergood@amc.com', '972-374-3182', '2794 Whispering Pines Circle ', 'Dallas', ' Texas ', '75207');

-- -----------------------------------------------------
-- DATA: cultures
-- -----------------------------------------------------
INSERT INTO cultures (name) 
VALUES 
('France'),
('USA'),
('Iran'),
('Italy'),
('Japan');

-- -----------------------------------------------------
-- DATA: breadProducts
-- -----------------------------------------------------
INSERT INTO breadProducts (name, unitPrice, count, netWeight, cultureID) 
VALUES 
('Baguette', 4.00, 1, 7.6, (select cultureID from cultures where name = 'France')),
('Banana Bread', 8.00, 1, 14, (select cultureID from cultures where name = 'USA')),
('Lavash', 3.00, 8, 9, (select cultureID from cultures where name = 'Iran')),
('Ciabatta', 8.00, 16, 11, (select cultureID from cultures where name = 'Italy')),
('Cornbread', 4.00, 16, 14.5, (select cultureID from cultures where name = 'USA'));

-- -----------------------------------------------------
-- DATA: sales
-- -----------------------------------------------------
INSERT INTO sales (customerID, saleTotal) 
VALUES 
(1, 1680.00),
(4, 500.00),
(3, 1160.00);

-- -----------------------------------------------------
-- DATA: soldProducts
-- -----------------------------------------------------
INSERT INTO soldProducts (saleID, productID, qtySold, lineTotal) 
VALUES 
(1, 2, 10, 80.00),
(1, 4, 200, 1600.00),
(2, 3, 100, 300.00),
(2, 1, 50, 200.00),
(3, 5, 290, 1160.00);

-- -----------------------------------------------------
-- DATA: allergens
-- -----------------------------------------------------
INSERT INTO allergens(name) 
VALUES 
('gluten'),
('wheat'),
('milk'),
('eggs'),
('soy'),
('yeast');

-- -----------------------------------------------------
-- DATA: allergensProduct
-- -----------------------------------------------------
INSERT INTO allergensProducts (productID, allergenID) 
VALUES 
(1, (select allergenID from allergens where name = 'gluten')),
(1, (select allergenID from allergens where name = 'wheat')),
(3, (select allergenID from allergens where name = 'wheat')),
(4, (select allergenID from allergens where name = 'wheat'));

-- Reset Foreign Key Checks
SET FOREIGN_KEY_CHECKS=1;
COMMIT;

