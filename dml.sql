z-- -------------------------------------------
-- FIND FOR DROP DOWN
-- -------------------------------------------

-- Find productID and name for Bread Products dropdown
SELECT productID, name FROM breadProducts; 

-- Find saleID for sales drop down
SELECT saleID from sales;

-- -------------------------------------------
-- READ
-- -------------------------------------------

-- Get all data for breadProducts table (added LEFT JOIN so no data point is missing.)
SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, breadProducts.count, 
breadProducts.netWeight, breadProducts.stock, cultures.name as Culture,
group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as "Allergen(s)"
FROM breadProducts
INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID
LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID
Group by breadProducts.productID;

-- Get all data for allergensProducts
SELECT allergensProducts.allergensProductID, breadProducts.name as "Bread Product", allergens.name as "Allergen"
FROM allergensProducts
LEFT JOIN breadProducts ON breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens ON allergensProducts.allergenID = allergens.allergenID
Group by allergensProducts.allergensProductID;

-- Get all data for sales
SELECT sales.saleID, customers.name as customer, sum(soldProducts.lineTotal) as "Sale Total"
FROM sales
LEFT JOIN customers ON sales.customerID = customers.customerID
LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID
Group by sales.saleID;

-- Get all data for sold roducts
SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as "Product Name",  soldProducts.qtySold, soldProducts.lineTotal
FROM soldProducts
LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID
LEFT JOIN sales on sales.saleID = soldProducts.saleID
GROUP by soldProducts.soldProductID;

-- Get all data for customers
SELECT customersID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers;
Or SELECT * FROM customers;

-- Get all data for allergens
SELECT allergensID, name FROM allergens; 

-- get all data for cultures
SELECT culturesID, name from cultures;

-- -------------------------------------------
-- SEARCH
-- -------------------------------------------

-- Search for breadProduct (Search BOX)
SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, breadProducts.count, 
breadProducts.netWeight, breadProducts.stock, cultures.name as Culture,
group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as "Allergen(s)"
FROM breadProducts
INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID
LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID
Where breadProduct.name = :breadnameInput
Group by breadProducts.productID;

-- Search for Sale (Search BOX)
SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as "Sale Total"
FROM sales
LEFT JOIN customers ON sales.customerID = customers.customerID
LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID
Where sales.saleID = :saleIDInput
Group by sales.saleID;

-- -------------------------------------------
-- CREATE/ADD
-- -------------------------------------------

-- Add Bread Product (minus allergens)
INSERT INTO breadProducts (name, unitPrice, count, netWeight, stock, cultureID) 
VALUES (:breadnameInput, :unitPriceInput, :countInput, :netWeightInput, :netstockInput, :cultureIDInput);

-- Part of Add Bread Product - Adding Allergens to the Intersection Table
INSERT INTO allergensProduct(productID, allergenID)
VALUES (:productIDInput, :allergenIDInput);

-- Add Sale (sales table)
INSERT INTO sales(customerID), saleTotal
VALUES (:customerIDInput, :saleTotal);

-- Add Sale (soldProducts Intersection Table)
INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal)
Values (:saleIDInput, productIDInput, qtySoldInput, lineTotalInput);

-- Add Customer
INSERT INTO customers (name, email, phoneNumber, streetAddress, city, state, zipCode)
VALUES (:nameInput, :emailInput, :phoneNumberInput, :streetAddressInput, :cityInput, :stateInput, :zipCodeInput);

-- Add Allergen
INSERT INTO allergens(name)
VALUES (:allergenIDInput);

-- Add Culture
INSERT INTO cultures(name)
VALUES (:cultureIDInput);

-- -------------------------------------------
-- UPDATE
-- -------------------------------------------

-- Update breadProduct
UPDATE breadProducts SET name=:breadnameInput, unitPrice=:unitPriceInput, count=:countInput, netWeight=:netWeightInput, 
stock=:netstockInput, cultureID:cultureIDInput
WHERE productID=:productID_from_dropdown;

-- Part of Update Bread Product - Adding Allergens to the Intersection Table
UPDATE allergensProduct SET allergenID=:allergenIDInput
WHERE productID = :productID_from_dropdown;

-- Update Sale (sales table)
UPDATE sales SET customerID = :customerIDInput
WHERE saleID = :saleID_from_dropdown;

-- Update Sale -- (soldProducts Interesection table)
UPDATE soldProducts SET productID=:productIDInput, qtySold=:qtySoldInput, lineTotal=:lineTotalInput
WHERE soldProductID = :soldProductID_from_dropdown;

-- Update customers
onclick="updateCustomers('customerID')"
SELECT * FROM customers WHERE customerID = :customersID_selected_from_browse_Customers_page;



-- -------------------------------------------
-- DELETE
-- -------------------------------------------

-- Delete Bread Product 
DELETE FROM breadProduct WHERE id=:productID_from_dropdown;

-- Delete Bread Product's connections to M:N (soldProducts)
DELETE FROM soldProducts WHERE productID=:productID_from_dropdown;

-- Delete Bread Product's connections to M:N (allergensProducts)
DELETE FROM allergensProduct WHERE productID=:productID_from_dropdown;

-- Delete Sales
DELETE FROM sales WHERE saleID=:saleID_from_dropdown;

-- Delete Sale's Connection to M:N (soldProducts)
DELETE FROM soldProducts WHERE saleID=:saleID_from_dropdown;

-- Delete customer
onclick="deleteCustomers('pid')" 
DELETE FROM customers WHERE pid = :CustomersID_selected_from_browse_Customers_page;

-- Delete allergen
onclick="deleteAllergens('pid')" 
DELETE FROM allergens WHERE pid = :AllergensID_selected_from_browse_allergens_page;

-- Delete culture
onclick="deleteCultures('pid')" 
DELETE FROM cultures WHERE pid = :CulturesID_selected_from_browse_Cultures_page;