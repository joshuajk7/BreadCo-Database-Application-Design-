# Originality:
# All CRUD and queries for all routes, and everything else that is not listed in the citations.

# Citation for Flask Starter file:
# Date: 11/16/2023
# Adapted from Starter App Guide
# Use: Starter for Layout and Routing Function Headers, wsgi.py gunicorn form.
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app

# Citation for db_connector.py file:
# Date: 11/15/2023
# Adapted from db_connector in Starter App
# Use: Reconfigured the query_execute for the current database.
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app

# Citation for Bootstrap Alert:
# Date: 12/9/2023
# Taken from Bootstrap Website
# Use: Used for alert flash messages
# Source URL: https://getbootstrap.com/docs/5.3/components/alerts/#dismissing

# Citation for database() route:
# Date: 12/05/2023
# Adapted from stackoverflow.com | Christopher Stamp
# Use: Root Directory access to open database ddl source file for reading
# Source URL: https://stackoverflow.com/questions/14825787/flask-how-to-read-a-file-in-application-root


from flask import Flask, render_template, json, redirect, jsonify
from flask_mysqldb import MySQL
from flask import request, url_for, flash
import database.db_connector as db_connector
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['SECRET_KEY'] = 'yadayadayadayada'

mysql = MySQL(app)

db_connection = db_connector.connect_to_database()

### Helper Functions ###
# -- Execute Query from Db_connector, but returns tuple.
def execute_query(query, query_params=()):
    db_connection = db_connector.connect_to_database()
    return db_connector.execute_query(db_connection, query, query_params)

### Home Page ###
# -- Home Page
@app.route('/')
def home():
    return render_template('home.html')


### Database Reset ###
# -- Reset the Database
@app.route("/database", methods=["POST", "GET"])
def database():

    # Citation for database() route:
    # Date: 12/05/2023
    # Adapted from stackoverflow.com | Christopher Stamp
    # Use: Root Directory access to open database ddl source file for reading
    # Source URL: https://stackoverflow.com/questions/14825787/flask-how-to-read-a-file-in-application-root

    # Open and load the file into readFile
    file = open(f'{app.root_path}/ddl.sql', 'r')
    readFile = file.read()
    file.close()

    # Split each queries by ;
    queries = readFile.split(';')

    # Iterate through queries.
    db_connection = db_connector.connect_to_database()
    for query in queries:
        db_connector.execute_query(db_connection, query)

    flash("Database successfully reset!")
    return redirect(url_for('home'))


### Bread Products ###
# -- breadProducts Page
@app.route("/breadProducts", methods=["POST", "GET"])
def breadProducts():

    if request.method == "GET":
        # DML: Get all data for displaying breadProducts table
        bread_products_query = (
            "SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, "
            "breadProducts.count, breadProducts.netWeight, cultures.name as Culture, "
            "group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as \"Allergen(s)\" "
            "FROM breadProducts "
            "INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID "
            "LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID "
            "LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID "
            "GROUP BY breadProducts.productID;"
        )
        breadProducts_results = execute_query(query=bread_products_query)

        # DML: Retrieve all allergens
        allergens_query = "SELECT allergenID, name FROM allergens;"
        allergens_results = execute_query(allergens_query)

        # DML: Get cultures query for breadProducts table
        cultures_query = "SELECT cultureID, name FROM cultures;"
        cultures_results = execute_query(cultures_query)

        # Render the template with breadProducts and the other results.    
        return render_template('breadProducts.html', breadProducts=breadProducts_results, allergens=allergens_results, cultures=cultures_results) 
    
    elif request.method == "POST":
        # Retrieve the the add product data
        name = request.form.get('name')
        unit_price = request.form.get('unitPrice')
        count = request.form.get('count')
        net_weight = request.form.get('netWeight')

        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))

        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # DML: Add Bread Product (minus allergens)
        insert_query = """
            INSERT INTO breadProducts (name, unitPrice, count, netWeight, cultureID) 
            VALUES (%s, %s, %s, %s, %s);
        """
        execute_query(query=insert_query, query_params=(name, unit_price, count, net_weight, selected_cultureID))
 
        # DML: Get next incrementable productID for allergensTable
        productID_query= "SELECT MAX(productID) from breadProducts;"
        result = execute_query(query=productID_query)
        productID = result.fetchone()[0]

        # DML: Part of Add Bread Product - Adding Allergens to the Intersection Table
        insert_query_allergensProduct = """
            INSERT INTO allergensProducts(productID, allergenID)
            VALUES (%s, %s);
        """
        for allergenID in selected_allergens:
            execute_query(insert_query_allergensProduct, query_params=(productID, allergenID))

        # Redirect to breadProducts page after adding a product
        return redirect('/breadProducts')


# -- delete breadProducts
@app.route("/breadProducts/<int:productID>", methods=["DELETE"])
def deleteProduct(productID):

    # DML: Delete Bread Product
    delete_breadProducts_query = "DELETE FROM breadProducts WHERE productID=%s;"
    execute_query(query=delete_breadProducts_query, query_params=(productID,))

    # Tell user that product was sucessfully deleted.
    response_data = {"message": "Product successfully deleted"}
    return jsonify(response_data), 200


# -- Loads up the data for the specified Product
@app.route("/editProduct/<int:productID>", methods=["GET"])
def editProduct(productID):
    
    # DML: Retrieve product details using productID
    product_query = "SELECT * FROM breadProducts WHERE productID = %s;"
    product_result = execute_query(query=product_query, query_params=(productID,))

    # DML: Retrieve allergens for the product
    allergens_query = "SELECT allergenID FROM allergensProducts WHERE productID = %s;"
    allergens_result = execute_query(query=allergens_query, query_params=(productID,))
    selected_allergens = allergens_result.fetchall()

    # DML: Retrieve all allergens
    all_allergens_query = "SELECT allergenID, name FROM allergens;"
    all_allergens_result = execute_query(query=all_allergens_query)

    # DML: Retrieve all cultures
    all_cultures_query = "SELECT * FROM cultures;"
    all_cultures_result = execute_query(query=all_cultures_query)

    # DML: Retrieve culture for the product
    culture_query = "SELECT cultureID FROM breadProducts WHERE productID =%s;"
    culture_result = execute_query(query=culture_query, query_params=(productID,))
    cultureID = culture_result.fetchone()

    # Render editProduct with the retrieved data
    return render_template("editProduct.html", product=product_result, selected_allergens=selected_allergens, all_allergens=all_allergens_result, all_cultures = all_cultures_result, selected_cultureID = cultureID, productID=productID)
    

# -- Updates the bread Product
@app.route("/updateProduct/<int:productID>", methods=["POST"])
def updateProduct(productID):

    try:
        # Retrieve the product's updated form data
        name = request.form.get('name')
        unit_price = request.form.get('unitPrice')
        count = request.form.get('count')
        net_weight = request.form.get('netWeight')
        
        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))

        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # DML: Update breadProduct
        update_query = "UPDATE breadProducts SET name=%s, unitPrice=%s, count=%s, netWeight=%s, cultureID=%s WHERE productID=%s;"
        execute_query(query=update_query, query_params=(name, unit_price, count, net_weight, selected_cultureID, productID))

        # Update allergens for the product
        ## Step 1: DML: Delete Bread Product's connections to M:N (allergensProducts)
        delete_allergens_query = "DELETE FROM allergensProducts WHERE productID=%s;"
        execute_query(query=delete_allergens_query, query_params=(productID,))

        # Step 2: DML: Add into allergensProducts
        selected_allergens = request.form.getlist('allergens[]')
        insert_allergens_query = "INSERT INTO allergensProducts (productID, allergenID) VALUES (%s, %s);"
        for allergenID in selected_allergens:
            execute_query(query=insert_allergens_query, query_params=(productID, allergenID))

        # Redirect to the breadProducts page after processessing the form
        response_data = {"message": "Product successfully updated"}
        return redirect('/breadProducts')

    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update product"}
            return jsonify(response_data), 500


### Customers ###
# -- Customers Page
@app.route("/customers", methods=['GET', 'POST'])
def customers():
    
    if request.method == "GET":
        # DML: Get all data for displaying customers table
        customers_query = "SELECT * FROM customers;"
        customers_results = execute_query(query=customers_query).fetchall()
        
        # DML: Get customerIDs associated with sales for key-constraints
        saleIDs_arr = []
        saleIDs_query = "SELECT customerID FROM sales;"
        saleIDs_query = execute_query(query=saleIDs_query)
        for arr in saleIDs_query:
            saleIDs_arr.append(arr[0])

        # Render the template with the customers and customerIDs associated with a sale.
        return render_template('customers.html', customers=customers_results, saleIDs=saleIDs_arr) 
    
    elif request.method == "POST":
        # Retrieve the form data for adding a customer
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        streetAddress = request.form.get('streetAddress')
        city = request.form.get('city')
        state = request.form.get('state')
        zipCode = request.form.get('zipCode')

        # DML: Add Customer
        query = "INSERT INTO customers (name, email, phoneNumber, streetAddress, city, state, zipCode) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cur = mysql.connection.cursor()
        cur.execute(query, (name, email, phoneNumber, streetAddress, city, state, zipCode))
        mysql.connection.commit()

        # Redirect to customers page after committing the addition of a customer.
        return redirect(('/customers'))

    return render_template('customers.html')


# -- Delete a Customer
@app.route("/customer/<int:customerID>", methods=["DELETE"])
def deleteCustomer(customerID):

    # DML: Delete customer
    delete_customers_query = "DELETE FROM customers WHERE customerID=%s;"
    execute_query(query=delete_customers_query, query_params=(customerID,))

    # Return success message for successfuly deletion of customer.
    response_data = {"message": "Customer successfully deleted"}
    return jsonify(response_data), 200


# -- Load a Customer's Information for an Update
@app.route("/editCustomer/<int:customerID>", methods=["GET"])
def editCustomer(customerID):

    # DML: Retrieve customer details using customerID
    customer_query = "SELECT * FROM customers where customerID=%s;"
    customer_result = execute_query(query=customer_query, query_params=(customerID,)).fetchall()

    # Render the edit form with loaded customer data
    return render_template("editCustomer.html", customerID=customerID, customer=customer_result)


# -- Update a Customer
@app.route("/updateCustomer/<int:customerID>", methods=["POST"])
def updateCustomer(customerID):
    try:
         # Retrieve form data from update form
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        streetAddress = request.form.get('streetAddress')
        city = request.form.get('city')
        state = request.form.get('state')
        zipCode = request.form.get('zipCode')
        
        # DML: Update customers
        update_query = "UPDATE customers SET name=%s, email=%s, phoneNumber=%s, streetAddress=%s, city=%s, state=%s, zipCode=%s WHERE customerID=%s;"
        execute_query(query=update_query, query_params=(name, email, phoneNumber, streetAddress, city, state, zipCode, customerID))

        # Redirect to customers after the update
        return redirect('/customers') 
    
    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update customer"}
            return jsonify(response_data), 500


### Sales & SoldProducts ###
# -- Sales and soldProducts Page
@app.route('/sales', methods=['GET', 'POST'])
def sales():

    if request.method == "GET":
        # DML: Get all data for sales
        query = "SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as 'Sale Total' FROM sales LEFT JOIN customers ON sales.customerID = customers.customerID LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID Group by sales.saleID;"
        sales_results = execute_query(query=query).fetchall()

        # DML: Get all data for soldProducts
        query = "SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as 'Product Name',  soldProducts.qtySold, soldProducts.lineTotal FROM soldProducts LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID LEFT JOIN sales on sales.saleID = soldProducts.saleID GROUP by soldProducts.soldProductID;"
        soldProducts_results = execute_query(query).fetchall()

        # DML: Retrieve customer name for sales
        query = "SELECT customerID, name from customers;"
        customers_results = execute_query(query=query).fetchall()

        # DML: Retrieve product name for sales
        query = "SELECT productID, name from breadProducts;"
        products_results = execute_query(query=query).fetchall()

        return render_template('sales.html', sales=sales_results, soldProducts=soldProducts_results, customers=customers_results, products=products_results, row=0)
        
    elif request.method == 'POST':

        # Check if user submits sale without any products
        if not request.form.get('products[]'):
           flash("No products added. Please add a product when you are submitting a sale.")
           return redirect('/sales#addSale')

        # Get the form data from adding a sale and a group of soldProducts
        customer_id = request.form.get('customer')
        products = request.form.getlist('products[]')
        quantities = request.form.getlist('quantities[]')

        # Check if sale includes repeated products
        sorted_products = sorted(products)
        for i in range(len(sorted_products)-1):
            if sorted_products[i] == sorted_products[i+1]:
                flash("Please do not add repeated products to the same sale.")
                return redirect('/sales#addSale')

        # Calculate lineTotal for each product
        line_totals = []
        for i in range(len(products)):
            # DML: Retrieve unit price from breadProducts for calculating lineTotal
            unitPrice_query = "SELECT unitPrice from breadProducts WHERE %s=productID;"
            unitPrice_result = execute_query(query=unitPrice_query, query_params=(products[i])).fetchone()[0]
            line_total = float(unitPrice_result) * float(quantities[i])
            line_totals.append(line_total)
        print(line_totals)
        
        # Calculate saleTotal
        saleTotal = 0
        for lineTotal in line_totals:
            saleTotal += lineTotal
        
        # DML: Add sale to sales table
        insert_sale_query = "INSERT INTO sales(customerID, saleTotal) VALUES (%s, %s)"
        execute_query(query=insert_sale_query, query_params=(customer_id, saleTotal))

        # DML: Retrieve incrementer saleID for soldProducts 
        saleID_query = "SELECT MAX(saleID) from sales;"
        saleID = execute_query(query=saleID_query).fetchone()[0]

        # DML: Add products to soldProducts intersection table
        for i in range(len(products)):
            insert_sold_product_query = "INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal) VALUES (%s, %s, %s, %s)"
            execute_query(query=insert_sold_product_query, query_params=(saleID, products[i], quantities[i], line_totals[i]))
        
        return redirect('sales')


# -- Delete a Sale
@app.route("/sales/<int:saleID>", methods=["DELETE"])
def deleteSale(saleID):

    # DML: Delete Sale's Connection to M:N (soldProducts)
    delete_soldProducts_query = "DELETE FROM soldProducts WHERE saleID = %s;"
    execute_query(query=delete_soldProducts_query, query_params=(saleID,))

    # DML: Delete Sale
    delete_sale_query = "DELETE FROM sales WHERE saleID = %s"
    execute_query(query=delete_sale_query, query_params=(saleID,))

    # Return message from successful deletion of a sale
    response_data = {"message": "Allergen successfully deleted"}
    return jsonify(response_data), 200


# -- Load a Sale for an Update
@app.route("/editSale/<int:saleID>", methods=["GET"])
def editSale(saleID):

    # DML: Retrieve sale details
    sale_query = "SELECT * FROM sales WHERE saleID = %s"
    sale_result = execute_query(query=sale_query, query_params=(saleID,)).fetchone()

    # DML: Retrieve soldProducts for the sale
    sold_products_query = "SELECT * FROM soldProducts WHERE saleID = %s"
    sold_products_result = execute_query(query=sold_products_query, query_params=(saleID,)).fetchall()

    # DML: Retrieve customer name for sales
    customers_query = "SELECT customerID, name FROM customers"
    customers = execute_query(query=customers_query).fetchall()

    # DML: Retrieve product name for sales
    products_query = "SELECT productID, name FROM breadProducts"
    products = execute_query(query=products_query).fetchall()

    # Render edit form with loaded data from the sale
    return render_template('editSale.html', sale=sale_result, soldProducts=sold_products_result, customers=customers, products=products, saleID=saleID)


# -- Update a Sale
@app.route("/updateSale/<int:saleID>", methods=["POST"])
def updateSale(saleID):

    try:
        # Retrieve form data from the updated edit form
        customerID = int(request.form.get('customerID'))
        soldProductIDs = [int(i) for i in request.form.getlist('soldProductIDs[]')]
        productIDs = [int(i) for i in request.form.getlist('productIDs[]')]
        quantitySolds = [int(i) for i in request.form.getlist('quantitySold[]')]
        print(customerID, soldProductIDs, productIDs, quantitySolds)

        # Auto-calculate line totals from the unit price in bread Products
        line_totals = []
        for i in range(len(soldProductIDs)):
            # DML: Retrieve unit price from breadProducts for calculating lineTotal in sales
            unitPrice_query = "SELECT unitPrice from breadProducts WHERE productID=%s;"
            unitPrice_result = execute_query(query=unitPrice_query, query_params=(productIDs[i],)).fetchone()[0]

            line_total = float(unitPrice_result) * float(quantitySolds[i])
            line_totals.append(line_total)

        # Calculate saleTotal
        saleTotal = 0
        for lineTotal in line_totals:
            saleTotal += lineTotal
        
        # DML: Update Sale
        update_sale_query = "UPDATE sales SET customerID=%s WHERE saleID=%s;"
        execute_query(query=update_sale_query, query_params=(customerID, saleID))

        # DML: Update products to soldProducts intersection table
        for i in range(len(soldProductIDs)):
            insert_sold_product_query = "UPDATE soldProducts SET productID=%s, qtySold=%s, lineTotal=%s WHERE soldProductID=%s"
            execute_query(query=insert_sold_product_query, query_params=(productIDs[i], quantitySolds[i], line_totals[i], soldProductIDs[i]))

        response_data = {"message": "Sale successfully updated"}
        return redirect('/sales')

    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update sale"}
            return jsonify(response_data), 500


### Cultures ###
# -- Cultures Page
@app.route("/cultures", methods=["POST", "GET"])
def cultures():

    if request.method == "GET":
        # DML: Retrieve all cultures | Display cultures Table
        cultures_query = "SELECT * FROM cultures;"
        cultures_results = execute_query(query=cultures_query)

        # Gather culture IDs that are currently present in a product
        breadIDs_arr = []
        # DML: Retrieve all cultureIDs present in a product
        breadIDs_query = "SELECT cultureID FROM breadProducts;"
        breadIDs_results = execute_query(query=breadIDs_query)
        for arr in breadIDs_results:
            breadIDs_arr.append(arr[0])

        # Render the template with the cultures
        return render_template('cultures.html', cultures=cultures_results, breadIDs=breadIDs_arr) 
    
    elif request.method == "POST":
        # Retrieve the form data from cultures
        name = request.form.get('name')

        # DML: Add Culture
        insert_query_cultures = "INSERT INTO cultures (name) VALUES (%s); " 
        cultures_results = execute_query(query=insert_query_cultures, query_params=(name,))

        # Redirect to cultures page after adding.
        return redirect('/cultures') 


# -- Delete a Culture
@app.route("/cultures/<int:culturesID>", methods=["DELETE"])
def deleteCultures(culturesID):

    # DML: Delete culture
    delete_cultures_query = "DELETE FROM cultures WHERE cultureID=%s;"
    execute_query(query=delete_cultures_query, query_params=(culturesID,))

    # Return success message for deletion of culture
    response_data = {"message": "Culture successfully deleted"}
    return jsonify(response_data), 200


### Allergens ### 
# -- Allergens Page
@app.route("/allergens", methods=["POST", "GET"])
def allergens():

    if request.method == "GET":
        # DML: Get all data for displaying allergens
        allergens_query = "SELECT * FROM allergens;"
        allergens_results = execute_query(query=allergens_query)

        # DML: Get all data for displaying allergensProducts
        allergensProducts_query = "SELECT allergensProducts.allergensProductID, breadProducts.name as 'Bread Product', allergens.name as Allergen FROM allergensProducts LEFT JOIN breadProducts ON breadProducts.productID = allergensProducts.productID LEFT JOIN allergens ON allergensProducts.allergenID = allergens.allergenID Group by allergensProducts.allergensProductID;"
        allergensProducts_results = execute_query(query=allergensProducts_query)

        # Render the template with the allergens and allergensProducts (intersection table)
        return render_template('allergens.html', allergens=allergens_results, allergensProducts=allergensProducts_results) 
    
    elif request.method == "POST":
        # Retrieve form data from add allergens
        name = request.form.get('name')

        # DML: Add Allergen
        insert_query_allergens = "INSERT INTO allergens (name) VALUES (%s); " 
        allergens_results = execute_query(query=insert_query_allergens, query_params=(name,))

        # Render allergens after adding an allergen
        return redirect('/allergens')


# -- Delete an Allergen
@app.route("/allergens/<int:allergenID>", methods=["DELETE"])
def deleteAllergen(allergenID):

    # DML: Delete allergen
    delete_allergens_query = "DELETE FROM allergens WHERE allergenID=%s;"
    execute_query(query=delete_allergens_query, query_params=(allergenID,))

    # Return success message for deletion of allergen
    response_data = {"message": "Allergen successfully deleted"}
    return jsonify(response_data), 200


# Listener
if __name__ == "__main__":

    app.run(port=54290, debug='TRUE')