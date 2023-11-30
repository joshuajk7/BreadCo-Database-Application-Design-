from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL
from database.db_credentials import host, user, passwd, db
import database.db_connector as db_connector
import os


app = Flask(__name__)

db_connection = db_connector.connect_to_database()

app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = passwd
app.config['MYSQL_DB'] = db

mysql = MySQL(app)

def execute_query(query, query_params=()):
    return db_connector.execute_query(db_connection, query, query_params)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/')
def home():
    return render_template("index.html")


#### Bread Product ####
@app.route("/breadProducts", methods=["POST", "GET"])
def breadProducts():
    if request.method == "GET":
        #This contains the list of scripts we want to show on the page. This is shown in the layout.html page
        # bread_products_query = "SELECT productID, name, unitPrice, count, netWeight, stock FROM breadProducts; "
        bread_products_query = (
            "SELECT breadProducts.productID, breadProducts.name, breadProducts.unitPrice, "
            "breadProducts.count, breadProducts.netWeight, breadProducts.stock, cultures.name as Culture, "
            "group_concat(allergens.name ORDER BY allergens.name SEPARATOR ', ') as \"Allergen(s)\" "
            "FROM breadProducts "
            "INNER JOIN cultures on breadProducts.cultureID = cultures.cultureID "
            "LEFT JOIN allergensProducts on breadProducts.productID = allergensProducts.productID "
            "LEFT JOIN allergens on allergensProducts.allergenID = allergens.allergenID "
            "GROUP BY breadProducts.productID;"
        )
        breadProducts_results = execute_query(query=bread_products_query)

        allergens_query = "SELECT allergenID, name FROM allergens;"
        allergens_results = execute_query(allergens_query)

        cultures_query = "SELECT cultureID, name FROM cultures;"
        cultures_results = execute_query(cultures_query)

        #Render the template with the breadProducts and certificate results we generated     
        return render_template('breadProducts.html', breadProducts=breadProducts_results, allergens=allergens_results, cultures=cultures_results) 
    
    elif request.method == "POST":
        # Retrieve other form data
        name = request.form.get('name')
        unit_price = request.form.get('unitPrice')
        count = request.form.get('count')
        net_weight = request.form.get('netWeight')
        stock = request.form.get('stock')

        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))
        print(selected_cultureID)

        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # Add Bread Product (minus allergens)
        insert_query = """
            INSERT INTO breadProducts (name, unitPrice, count, netWeight, stock, cultureID) 
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        execute_query(query=insert_query, query_params=(name, unit_price, count, net_weight, stock, selected_cultureID))
 
        # Get productID
        productID_query= "SELECT LAST_INSERT_ID();"
        result = execute_query(query=productID_query)
        productID = result.fetchone()[0]

        # Part of Add Bread Product - Adding Allergens to the Intersection Table
        insert_query_allergensProduct = """
            INSERT INTO allergensProducts(productID, allergenID)
            VALUES (%s, %s);
        """
        for allergenID in selected_allergens:
            execute_query(insert_query_allergensProduct, query_params=(productID, allergenID))

        # Redirect or render a respose
        return redirect('/breadProducts') # Redirect to the breadProducts page after processessing the form

@app.route("/breadProducts/<int:productID>", methods=["DELETE"])
def deleteProduct(productID):
    # Delete Bread Product's connections to M:N (allergensProducts)
    delete_allergensProducts_query = "DELETE FROM allergensProducts WHERE productID=%s;"
    execute_query(query=delete_allergensProducts_query, query_params=(productID,))

    # Then Delete Bread Product 
    delete_breadProducts_query = "DELETE FROM breadProducts WHERE productID=%s;"
    execute_query(query=delete_breadProducts_query, query_params=(productID,))

    response_data = {"message": "Product successfully deleted"}
    return jsonify(response_data), 200

@app.route("/editProduct/<int:productID>", methods=["GET"])
def editProduct(productID):
    # Retrieve product details using productID
    product_query = "SELECT * FROM breadProducts WHERE productID = %s;"
    product_result = execute_query(query=product_query, query_params=(productID,))

    # Retrieve allergens for the product
    allergens_query = "SELECT allergenID FROM allergensProducts WHERE productID = %s;"
    allergens_result = execute_query(query=allergens_query, query_params=(productID,))
    selected_allergens = allergens_result.fetchall()
    # selected_allergens example: ((2,), (3,))

    # Retrieve all allergens
    all_allergens_query = "SELECT allergenID, name FROM allergens;"
    all_allergens_result = execute_query(query=all_allergens_query)

    # Retrieve all cultures
    all_cultures_query = "SELECT * FROM cultures;"
    all_cultures_result = execute_query(query=all_cultures_query)

    # Retrieve culture for the product
    culture_query = "SELECT cultureID FROM breadProducts WHERE productID =%s;"
    culture_result = execute_query(query=culture_query, query_params=(productID,))
    cultureID = culture_result.fetchone()
    # Render the edit form with product details

    return render_template("editProduct.html", product=product_result, selected_allergens=selected_allergens, all_allergens=all_allergens_result, all_cultures = all_cultures_result, selected_cultureID = cultureID, productID=productID)
    
@app.route("/updateProduct/<int:productID>", methods=["POST"])
def updateProduct(productID):
    try:
        # Retrieve form data
        name = request.form.get('name')
        unit_price = request.form.get('unitPrice')
        count = request.form.get('count')
        net_weight = request.form.get('netWeight')
        stock = request.form.get('stock')
        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))
        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # Update product details
        update_query = "UPDATE breadProducts SET name=%s, unitPrice=%s, count=%s, netWeight=%s, stock=%s, cultureID=%s WHERE productID=%s;"
        execute_query(query=update_query, query_params=(name, unit_price, count, net_weight, stock, selected_cultureID, productID))


        # Update allergens for the product
        # Step 1: Delete existing allergens
        delete_allergens_query = "DELETE FROM allergensProducts WHERE productID=%s;"
        execute_query(query=delete_allergens_query, query_params=(productID,))

        # Step 2: Insert new allergens
        selected_allergens = request.form.getlist('allergens[]')
        insert_allergens_query = "INSERT INTO allergensProducts (productID, allergenID) VALUES (%s, %s);"
        for allergenID in selected_allergens:
            execute_query(query=insert_allergens_query, query_params=(productID, allergenID))

        response_data = {"message": "Product successfully updated"}
        # return jsonify(response_data), 200
        return redirect('/breadProducts') # Redirect to the breadProducts page after processessing the form


    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update product"}
            return jsonify(response_data), 500

#### Allergens ####
@app.route("/allergens", methods=["POST", "GET"])
def allergens():
    if request.method == "GET":
        allergens_query = "SELECT * FROM allergens;"
        allergens_results = execute_query(query=allergens_query)

        #Render the template with the allergens
        return render_template('allergens.html', allergens=allergens_results) 
    
    elif request.method == "POST":
        # Retrieve form data
        name = request.form.get('name')

        # Part of Add Allergen - Adding Allergens to the Intersection Table
        insert_query_allergens = "INSERT INTO allergens (name) VALUES (%s); " 
        allergens_results = execute_query(query=insert_query_allergens, query_params=(name,))

        # Redirect or render a respose
        return redirect('/allergens') # Redirect to the allergens page after processessing the form

@app.route("/allergens/<int:allergenID>", methods=["DELETE"])
def deleteAllergen(allergenID):
    # Delete allergen's connections to M:N (allergensProducts)
    delete_allergensProducts_query = "DELETE FROM allergensProducts WHERE allergenID=%s;"
    execute_query(query=delete_allergensProducts_query, query_params=(allergenID,))

    # Then Delete allergen (allergens)
    delete_allergens_query = "DELETE FROM allergens WHERE allergenID=%s;"
    execute_query(query=delete_allergens_query, query_params=(allergenID,))

    response_data = {"message": "Allergen successfully deleted"}
    return jsonify(response_data), 200

#### Cultures ####
@app.route("/cultures", methods=["POST", "GET"])
def cultures():
    if request.method == "GET":
        cultures_query = "SELECT * FROM cultures;"
        cultures_results = execute_query(query=cultures_query)

        #Render the template with the cultures
        return render_template('cultures.html', cultures=cultures_results) 
    
    elif request.method == "POST":
        # Retrieve form data
        name = request.form.get('name')

        # Add culture
        insert_query_cultures = "INSERT INTO cultures (name) VALUES (%s); " 
        cultures_results = execute_query(query=insert_query_cultures, query_params=(name,))

        # Redirect or render a respose
        return redirect('/cultures') # Redirect to the cultures page after processessing the form

@app.route("/cultures/<int:culturesID>", methods=["DELETE"])
def deleteCultures(culturesID):
    # Then Delete culture (cultures)
    delete_cultures_query = "DELETE FROM cultures WHERE cultureID=%s;"
    execute_query(query=delete_cultures_query, query_params=(culturesID,))

    response_data = {"message": "Culture successfully deleted"}
    return jsonify(response_data), 200

#### Sales ###
@app.route('/sales', methods=['GET', 'POST'])
def sales():

    if request.method == "GET":
        # Display Table Data for Sales and SoldProducts
        query = "SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as 'Sale Total' FROM sales LEFT JOIN customers ON sales.customerID = customers.customerID LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID Group by sales.saleID;"
        sales_results = execute_query(query=query).fetchall()

        query = "SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as 'Product Name',  soldProducts.qtySold, soldProducts.lineTotal FROM soldProducts LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID LEFT JOIN sales on sales.saleID = soldProducts.saleID GROUP by soldProducts.soldProductID;"
        soldProducts_results = execute_query(query).fetchall()

        query = "SELECT customerID, name from customers;"
        customers_results = execute_query(query=query).fetchall()

        query = "SELECT productID, name from breadProducts;"
        products_results = execute_query(query=query).fetchall()

        return render_template('sales.html', sales=sales_results, soldProducts=soldProducts_results, customers=customers_results, products=products_results)
        
    elif request.method == 'POST':
        # Get Form Data
        customer_id = request.form.get('customer')
        products = request.form.getlist('products[]')
        quantities = request.form.getlist('quantities[]')

        # Calculate lineTotal for each product
        line_totals = []
        for i in range(len(products)):
            unitPrice_query = "SELECT unitPrice from breadProducts WHERE %s=productID;"
            unitPrice_result = execute_query(query=unitPrice_query, query_params=(products[i])).fetchone()[0]
            line_total = float(unitPrice_result) * float(quantities[i])
            line_totals.append(line_total)
        print(line_totals)
        
        # Calculate saleTotal
        saleTotal = 0
        for lineTotal in line_totals:
            saleTotal += lineTotal
        
        # Add sale to sales Table
        insert_sale_query = "INSERT INTO sales(customerID, saleTotal) VALUES (%s, %s)"
        execute_query(query=insert_sale_query, query_params=(customer_id, saleTotal))

        # Retrieve saleID 
        saleID_query = "SELECT LAST_INSERT_ID();"
        saleID = execute_query(query=saleID_query).fetchone()[0]


        # Add products to soldProducts intersection table
        for i in range(len(products)):
            insert_sold_product_query = "INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal) VALUES (%s, %s, %s, %s)"
            execute_query(query=insert_sold_product_query, query_params=(saleID, products[i], quantities[i], line_totals[i]))
        
        return redirect('sales')

    # return render_template('sales.html', sales=sales_results, soldProducts=soldProducts_results, customers=customers_results, products= products_results,count=sales_create_count, update_sales_results=update_sales_results, sale_id = int(saleID))

@app.route("/sales/<int:saleID>", methods=["DELETE"])
def deleteSale(saleID):
    # Delete from soldProducts Intersection table
    delete_soldProducts_query = "DELETE FROM soldProducts WHERE saleID = %s;"
    execute_query(query=delete_soldProducts_query, query_params=(saleID,))

    # Delete from sales table
    delete_sale_query = "DELETE FROM sales WHERE saleID = %s"
    execute_query(query=delete_sale_query, query_params=(saleID,))

    response_data = {"message": "Allergen successfully deleted"}
    return jsonify(response_data), 200

@app.route("/editSale/<int:saleID>", methods=["GET"])
def editSale(saleID):
    # Retrieve the sale details
    sale_query = "SELECT * FROM sales WHERE saleID = %s"
    sale_result = execute_query(query=sale_query, query_params=(saleID,)).fetchone()

    # Retrieve the soldProducts for the sale
    sold_products_query = "SELECT * FROM soldProducts WHERE saleID = %s"
    sold_products_result = execute_query(query=sold_products_query, query_params=(saleID,)).fetchall()

    # Retrieve other necessary data (customers, products, etc.)
    customers_query = "SELECT customerID, name FROM customers"
    customers = execute_query(query=customers_query).fetchall()

    products_query = "SELECT productID, name FROM breadProducts"
    products = execute_query(query=products_query).fetchall()

    return render_template('editSale.html', sale=sale_result, soldProducts=sold_products_result, customers=customers, products=products, saleID=saleID)

@app.route("/updateSale/<int:saleID>", methods=["POST"])
def updateSale(saleID):
    try:
        # Retrieve form data
        customerID = int(request.form.get('customerID'))
        soldProductIDs = [int(i) for i in request.form.getlist('soldProductIDs[]')]
        productIDs = [int(i) for i in request.form.getlist('productIDs[]')]
        quantitySolds = [int(i) for i in request.form.getlist('quantitySold[]')]
        print(customerID, soldProductIDs, productIDs, quantitySolds)

        line_totals = []
        for i in range(len(soldProductIDs)):
            unitPrice_query = "SELECT unitPrice from breadProducts WHERE productID=%s;"
            unitPrice_result = execute_query(query=unitPrice_query, query_params=(soldProductIDs[i],)).fetchone()[0]

            line_total = float(unitPrice_result) * float(quantitySolds[i])
            line_totals.append(line_total)

        # Calculate saleTotal
        saleTotal = 0
        for lineTotal in line_totals:
            saleTotal += lineTotal
        
        # UPDATE sale to sales Table
        update_sale_query = "UPDATE sales SET customerID=%s WHERE saleID=%s;"
        execute_query(query=update_sale_query, query_params=(customerID, saleID))


        # Add products to soldProducts intersection table
        for i in range(len(soldProductIDs)):
            insert_sold_product_query = "UPDATE soldProducts SET productID=%s, qtySold=%s, lineTotal=%s WHERE soldProductID=%s"
            execute_query(query=insert_sold_product_query, query_params=(productIDs[i], quantitySolds[i], line_totals[i], soldProductIDs[i]))

        response_data = {"message": "Product successfully updated"}
        # return jsonify(response_data), 200
        return redirect('/sales') # Redirect to the breadProducts page after processessing the form

    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update product"}
            return jsonify(response_data), 500

@app.route("/customers", methods=['GET', 'POST'])
def customers():
    
    if request.method == "GET":
        
        # Display Customers Table
        customers_query = "SELECT * FROM customers;"
        customers_results = execute_query(query=customers_query).fetchall()

        #Render the template with the customers
        return render_template('customers.html', customers=customers_results) 
    
    elif request.method == "POST":
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        streetAddress = request.form.get('streetAddress')
        city = request.form.get('city')
        state = request.form.get('state')
        zipCode = request.form.get('zipCode')
        query = "INSERT INTO customers (name, email, phoneNumber, streetAddress, city, state, zipCode) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cur = mysql.connection.cursor()
        cur.execute(query, (name, email, phoneNumber, streetAddress, city, state, zipCode))
        mysql.connection.commit()

        return redirect(('/customers'))

    return render_template('customers.html', customers=customers_results, load=load, customers_in_sales=customers_in_sales)

# -- Delete a Customer
@app.route("/customer/<int:customerID>", methods=["DELETE"])
def deleteCustomer(customerID):
    # Then Delete Customer (Customer)
    delete_customers_query = "DELETE FROM customers WHERE customerID=%s;"
    execute_query(query=delete_customers_query, query_params=(customerID,))

    response_data = {"message": "Customer successfully deleted"}
    return jsonify(response_data), 200


@app.route("/editCustomer/<int:customerID>", methods=["GET"])
def editCustomer(customerID):
    # Retrieve customer details using customerID
    customer_query = "SELECT * FROM customers where customerID=%s;"
    customer_result = execute_query(query=customer_query, query_params=(customerID,)).fetchall()

    return render_template("editCustomer.html", customerID=customerID, customer=customer_result)

@app.route("/updateCustomer/<int:customerID>", methods=["POST"])
def updateCustomer(customerID):
    try:
         # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        streetAddress = request.form.get('streetAddress')
        city = request.form.get('city')
        state = request.form.get('state')
        zipCode = request.form.get('zipCode')
        
        upadate_query = "UPDATE customers SET name=%s, email=%s, phoneNumber=%s, streetAddress=%s, city=%s, state=%s, zipCode=%s WHERE customerID=%s;"
        execute_query(query=upadate_query, query_params=(name, email, phoneNumber, streetAddress, city, state, zipCode, customerID))

        # Redirect or render a respose
        return redirect('/customers') # Redirect to the customers page after processessing the form
    
    except Exception as e:
            # Handle exceptions, log the error, and return an appropriate response
            print(f"Error updating product: {e}")
            response_data = {"error": "Failed to update product"}
            return jsonify(response_data), 500
    
@app.route('/db-test')
def test_database_connection():
    print("Executing a sample query on the database using the credentials from db_credentials.py")
    db_connection = connect_to_database()
    query = "SELECT * from breadProducts;"
    result = execute_query(db_connection, query);
    return result



# @app.errorhandler(404)
# def page_not_found(error): 
#     return render_template('404.html')

# @app.errorhandler(500)
# def page_not_found(error):
#     return render_template('500.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112)) 
    #                                 ^^^^
    #              You can replace this number with any valid port
    
    app.run(port=port, debug=True) 
