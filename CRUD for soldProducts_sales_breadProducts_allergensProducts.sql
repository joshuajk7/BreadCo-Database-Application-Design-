-- Find productID and name for Bread Products dropdown
SELECT productID, name FROM breadProducts 

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

-- Get all data for sold Products
SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as "Product Name",  soldProducts.qtySold, soldProducts.lineTotal
FROM soldProducts
LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID
LEFT JOIN sales on sales.saleID = soldProducts.saleID
GROUP by soldProducts.soldProductID;


-- Search for breadProduct
SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, breadProducts.count, 
breadProducts.netWeight, breadProducts.stock, cultures.name as Culture,
group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as "Allergen(s)"
FROM breadProducts
INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID
LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID
LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID
Where breadProduct.name = :breadnameInput
Group by breadProducts.productID;

-- Search for Sale
SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as "Sale Total"
FROM sales
LEFT JOIN customers ON sales.customerID = customers.customerID
LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID
Where sales.saleID = :saleIDInput
Group by sales.saleID;

-- Add Bread Product (minus allergens)
INSERT INTO breadProducts (name, unitPrice, count, netWeight, stock, cultureID) 
VALUES (:breadnameInput, :unitPriceInput, :countInput, :netWeightInput, :netstockInput, :cultureIDInput);

-- Part of Add Bread Product - Adding Allergens to the Intersection Table
INSERT INTO allergensProduct(productID, allergenID)
VALUES (:productIDInput, :allergenIDInput);

-- Add Sale (minus sale total)
INSERT INTO sales(customerID)
VALUES (:customerIDInput);

-- Part of Adding Sale - Adding Sold Products to the Intersection Table
INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal)
Values (:saleIDInput, productIDInput, qtySoldInput, lineTotalInput);

-- Update breadProduct
UPDATE breadProducts SET name=:breadnameInput, unitPrice=:unitPriceInput, count=:countInput, netWeight=:netWeightInput, 
stock=:netstockInput, cultureID:cultureIDInput
WHERE id=:productID_from_dropdown;

-- Part of Update Bread Product - Adding Allergens to the Intersection Table
UPDATE allergensProduct SET allergenID=:allergenIDInput
WHERE id = :productID_from_dropdown;

-- Update Sale
UPDATE sales SET customer=:customerIDInput
WHERE id=:saleID_from_dropdown;

-- Update Sale -- Adding SaleID, Product Name, Quatnity Sold, Line Total to Interesection table
UPDATE sales SET productID=:productIDInput, qtySold=:qtySoldInput, lineTotal=:lineTotalInput
WHERE id=:saleID_from_dropdown;

-- Delete Bread Product 
DELETE FROM breadProduct WHERE id=:productID_from_dropdown;

-- Delete Bread Product's connections to M:N (soldProducts)
DELETE FROM soldProducts WHERE productID=:productID_from_dropdown;

-- Delete Bread Product's connections to M:N (allergensProducts)
DELETE FROM allergensProduct WHERE productID=:productID_from_dropdown;

-- Delete Sales
DELETE FROM saleID WHERE saleID=:saleID_from_dropdown;

-- Delete Sale's Connection to M:N (soldProducts)
DELETE FROM soldProducts WHERE saleID=:saleID_from_dropdown;