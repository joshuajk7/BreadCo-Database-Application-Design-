-- -------------------------------------------
-- READ/SELECT
-- -------------------------------------------

-- Get all data for displaying breadProducts table (added LEFT JOIN so no data point is missing.)
SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, breadProducts.count, 
breadProducts.netWeight, breadProducts.stock, cultures.name as Culture,
group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as "Allergen(s)"
FROM breadProducts
INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID
LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID
Group by breadProducts.productID;

-- Get cultures query for breadProducts table
SELECT cultureID, name FROM cultures;

-- Get next incrementable productID for allergensTable
SELECT MAX(productID) from breadProducts;

-- Retrieve product details using productID
SELECT * FROM breadProducts WHERE productID = :selectedEditProductID;

-- Retrieve allergens for the product
SELECT allergenID FROM allergensProducts WHERE productID = :selectedEditProductID;

-- Retrieve all allergens
SELECT allergenID, name FROM allergens;

-- Retrieve all cultures
SELECT * FROM cultures;

-- Retrieve culture for the product
SELECT cultureID FROM breadProducts WHERE productID = :selectedEditProductID;

-- Retrieve all cultureIDs present in a product
SELECT cultureID FROM breadProducts;

-- Get all data for displaying allergensProducts
SELECT allergensProducts.allergensProductID, breadProducts.name as "Bread Product", allergens.name as Allergen
FROM allergensProducts
LEFT JOIN breadProducts ON breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens ON allergensProducts.allergenID = allergens.allergenID
Group by allergensProducts.allergensProductID;

-- Get all data for sales
SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as "Sale Total"
FROM sales
LEFT JOIN customers ON sales.customerID = customers.customerID
LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID
Group by sales.saleID;

-- Retrieve customer name for sales
SELECT customerID, name from customers;

-- Retrieve product name for sales
SELECT productID, name from breadProducts;

-- Retrieve unit price from breadProducts for calculating lineTotal in sales
SELECT unitPrice from breadProducts WHERE productID = :selectedSaleProductID

-- Retrieve incrementer saleID for soldProducts
SELECT MAX(saleID) from sales;

-- Retrieve sale details
SELECT * FROM sales WHERE saleID = :selectedEditSaleID;

-- Retrieve soldProducts for the sale
SELECT * FROM soldProducts WHERE saleID = :selectedEditSaleID;

-- Get all data for soldProducts
SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as "Product Name",  soldProducts.qtySold, soldProducts.lineTotal
FROM soldProducts
LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID
LEFT JOIN sales on sales.saleID = soldProducts.saleID
GROUP by soldProducts.soldProductID;

-- Get all data for displaying customers table
SELECT * FROM customers;

-- Get customerIDs associated with sales for key-constraints
SELECT customerID FROM sales;

-- Retrieve customer details using customerID
SELECT * FROM customers where customerID= :selectedEditCustomerID;

-- Get all data for displaying allergens
SELECT * FROM allergens; 


-- -------------------------------------------
-- CREATE/ADD
-- -------------------------------------------

-- Add Bread Product (minus allergens)
INSERT INTO breadProducts (name, unitPrice, count, netWeight, stock, cultureID) 
VALUES (:breadnameInput, :unitPriceInput, :countInput, :netWeightInput, :netstockInput, :cultureIDInput);

-- Part of Add Bread Product - Adding Allergens to the Intersection Table
INSERT INTO allergensProduct(productID, allergenID)
VALUES (:productIDInput, :allergenIDInput);

-- Add Sale to sales table
INSERT INTO sales(customerID, saleTotal)
VALUES (:customerIDInput, :saleTotalCalc);

-- Add products to soldProducts intersection table
INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal)
Values (:saleIDInput, :productIDInput, :qtySoldInput, :lineTotalInput);

-- Add Customer
INSERT INTO `customers` (`customerID`, `name`, `email`, `phoneNumber`, `streetAddress`, `city`, `state`, `zipCode`) 
VALUES (':customerIDinput', ':nameInput', ':emailInput', ':phoneNumberInput', ':streetAddressInput', ':cityInput', ':stateInput', ‘:zipCodeInput’);

-- Add Allergen
INSERT INTO allergens(name)
VALUES (:allergenIDInput);

-- Add Culture
INSERT INTO cultures(name)
VALUES ( :cultureIDInput);


-- -------------------------------------------
-- UPDATE
-- -------------------------------------------

-- Update breadProduct
UPDATE breadProducts SET name=:breadnameInput, unitPrice=:unitPriceInput, count=:countInput, netWeight=:netWeightInput, 
stock=:netstockInput, cultureID:cultureIDInput
WHERE id=:productID_from_dropdown;

-- Update Sale
UPDATE sales SET customer= :customerIDInput
WHERE saleID= :saleID_from_dropdown;

-- Update products to soldProducts intersection table
UPDATE soldProducts SET productID= :productIDInput, qtySold= :qtySoldInput, lineTotal= :lineTotalInput 
WHERE soldProductID= :selectedUpdateSoldProductID;

-- Update customers
UPDATE customers 
SET name= :nameInput, email= :emailInput, phoneNumber= :phoneInput, streetAddress= :streetInput, city= :cityInput, state= :stateInput, zipCode= :zipInput 
WHERE customerID= :selectedUpdateCustomersID


-- -------------------------------------------
-- DELETE
-- -------------------------------------------

-- Delete Bread Product 
DELETE FROM breadProduct WHERE id= :deleteBreadProductID;

-- Delete Bread Product's connections to M:N (allergensProducts)
DELETE FROM allergensProducts WHERE productID=:productID_from_dropdown;

-- Delete Sale
DELETE FROM saleID WHERE saleID= :deleteSaleID;

-- Delete Sale's Connection to M:N (soldProducts)
DELETE FROM soldProducts WHERE saleID=:saleID_from_dropdown;

-- Delete customer
DELETE FROM customers WHERE customerID = :deleteCustomerID;

-- Delete allergen
DELETE FROM allergens WHERE allergenID = :deleteAllergenID;

-- Delete culture
DELETE FROM cultures WHERE cultureID= :deleteCultureID;