from flask import Flask, render_template, json, redirect, jsonify
from flask_mysqldb import MySQL
from flask import request, url_for
import database.db_connector as db_connector
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #last 4 of onid
app.config['MYSQL_DB'] = 'project_sample'
#app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

# Citation: 
db_connection = db_connector.connect_to_database()

## Helper Functions
# -- Execute Query from Db_connector, but returns tuple.
def execute_query(query, query_params=()):
    db_connection = db_connector.connect_to_database()
    return db_connector.execute_query(db_connection, query, query_params)

# -- Execute Query from db_connector, but returns dictionary instead.
def execute_query_dict(query, query_params=()):
    db_connection = db_connector.connect_to_database()
    return db_connector.execute_query_dict(db_connection, query, query_params)


## Routes

# -- Home Page
## Returns User Home
@app.route('/')
def home():
    return render_template('home.html')


### Bread Products ###
# -- breadProducts Page
@app.route("/breadProducts", methods=["POST", "GET"])
def breadProducts():
    if request.method == "GET":
        #This contains the list of scripts we want to show on the page. This is shown in the layout.html page
        # bread_products_query = "SELECT productID, name, unitPrice, count, netWeight FROM breadProducts; "
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

        print(breadProducts_results)

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

        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))
        print(selected_cultureID)

        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # Add Bread Product (minus allergens)
        insert_query = """
            INSERT INTO breadProducts (name, unitPrice, count, netWeight, cultureID) 
            VALUES (%s, %s, %s, %s, %s);
        """
        execute_query(query=insert_query, query_params=(name, unit_price, count, net_weight, selected_cultureID))
 
        # Get productID
        productID_query= "SELECT MAX(productID) from breadProducts;"
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


# -- delete breadProducts
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


# -- edit breadProducts
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
    

# -- update breadProducts    
@app.route("/updateProduct/<int:productID>", methods=["POST"])
def updateProduct(productID):
    try:
        # Retrieve form data
        name = request.form.get('name')
        unit_price = request.form.get('unitPrice')
        count = request.form.get('count')
        net_weight = request.form.get('netWeight')
        # Retrieve selected cultureID 
        selected_cultureID =  int(request.form.get('cultureID'))
        # Retrieve selected allergens as a list
        selected_allergens = request.form.getlist('allergens[]')

        # Update product details
        update_query = "UPDATE breadProducts SET name=%s, unitPrice=%s, count=%s, netWeight=%s, cultureID=%s WHERE productID=%s;"
        execute_query(query=update_query, query_params=(name, unit_price, count, net_weight, selected_cultureID, productID))


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


### Customers ###
# -- Customers Page
@app.route("/customers", methods=['GET', 'POST'])
def customers(load=False):
    
    # Display Customers Table
    query = "SELECT customerID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers"
    customers_results = execute_query_dict(query=query).fetchall()

    # Grab series of sales ID to cross refence with Delete (fix dml reflect this query)
    customers_in_sales = []
    query = "SELECT customerID FROM sales;"
    results = execute_query_dict(query=query).fetchall()

    for dict in results:
        customers_in_sales.append(dict['customerID'])

    if request.method == 'POST':
        # Adding a Customer

        ## Commiting Adding to a Customer
        if request.form.get('addCustomer'):
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

            return redirect(url_for('customers'))
    
        # Updating a Customer
        # Load a Customer
        if request.form.get('loadCustomer'):
            customerID = int(request.form.get('loadedCustomer'))
            query = f"SELECT customerID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers WHERE customerID = { customerID };"
            load = execute_query_dict(query=query).fetchall()

        # Commiting Updating a Customer to the Database
        if request.form.get('updateCustomer'):
            customerID = request.form.get('customerID')
            name = request.form.get('name')
            email = request.form.get('email')
            phoneNumber = request.form.get('phoneNumber')
            streetAddress = request.form.get('streetAddress')
            city = request.form.get('city')
            state = request.form.get('state')
            zipCode = request.form.get('zipCode')
            query = "UPDATE customers SET name = %s, email = %s, phoneNumber = %s, streetAddress = %s, city = %s, state = %s, zipCode = %s WHERE customerID = %s;"
            cur = mysql.connection.cursor()
            cur.execute(query, (name, email, phoneNumber, streetAddress, city, state, zipCode, customerID))
            mysql.connection.commit()
        
            return redirect(url_for('customers'))
    

    return render_template('customers.html', customers=customers_results, load=load, customers_in_sales=customers_in_sales)


# -- Delete a customer
@app.route("/delete_customers/<int:customerID>")
def delete_customers(customerID):
    ## Delete from customers
    query = "DELETE FROM customers where customerID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (customerID,))
    mysql.connection.commit()

    return redirect("/customers")


### Sales & SoldProducts ###
# -- Sales Page
@app.route('/sales', methods=['GET', 'POST'])
def sales(sales_create_count=1, update_sales_results=0, saleID=0):

    # Display Table Data for Sales and SoldProducts
    query = "SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as 'Sale Total' FROM sales LEFT JOIN customers ON sales.customerID = customers.customerID LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID Group by sales.saleID;"
    sales_results = execute_query_dict(query=query).fetchall()

    query = "SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as 'Product Name',  soldProducts.qtySold, soldProducts.lineTotal FROM soldProducts LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID LEFT JOIN sales on sales.saleID = soldProducts.saleID GROUP by soldProducts.soldProductID;"
    soldProducts_results = execute_query_dict(query).fetchall()

    query = "SELECT customerID, name from customers;"
    customers_results = execute_query_dict(query=query).fetchall()

    query = "SELECT productID, name from breadProducts;"
    products_results = execute_query_dict(query=query).fetchall()
    
    if request.method == 'POST':
        # Add a Sale Feature
        ## Add and Remove Product from Add Sale
        if request.form.get('soldProduct'):
            sales_create_count=int(request.form['soldProduct'])
        elif request.form.get('removeProduct'):
            sales_create_count=int(request.form['removeProduct'])

        elif request.form.get('submitSale'):
            ### Gather Add Data, put all data in array. Check for Discrepancies.
            sales_create_count = int(request.form['submitSale'])
            customer = request.form['customer']
            name_arr = []
            qtySold_arr = []
            lineTotal_arr = []

            for i in range(1, sales_create_count+1):
                name_arr.append(request.form.get("bread_"+str(i)))
                qtySold_arr.append(request.form.get("qtySold_"+str(i)))
                lineTotal_arr.append(round(float(request.form.get("lineTotal_"+str(i))), 2))

            ### Add into Sale
            query = "INSERT INTO sales (customerID, saleTotal) VALUES (%s, %s);"
            cur = mysql.connection.cursor()
            cur.execute(query, (customer, sum(lineTotal_arr)))
            mysql.connection.commit()
            
            ### Add into soldProducts
            testing = []
            for i in range(1, sales_create_count+1):
                #### Get SaleID from Recent Insert
                query = "SELECT max(saleID) from sales;"
                saleID = execute_query_dict(query=query).fetchall()
                saleID = saleID[0]['max(saleID)']

                query = "INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal) Values (%s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                productID = execute_query_dict(query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" ).fetchall()
                productID = productID[0]['productID']  # [{:}] list of dictionaries format.
                cur.execute(query, (saleID, productID, qtySold_arr[i-1], lineTotal_arr[i-1]))
                mysql.connection.commit()

            return redirect(url_for('sales'))
        
        # Update a Sale Intro 
        elif request.form.get('saleID'):
            saleID = request.form.get('saleID')
            query = f"SELECT * from soldProducts where saleID = {saleID};"
            update_sales_results = execute_query_dict(query=query)

        # Gather Information to Update
        elif request.form.get('updateLength'):
            boxes = int(request.form.get('updateLength'))
            saleID = int(request.form.get('updateSaleID'))
            customerID = request.form.get('customer')
            name_arr = []
            qtySold_arr = []
            lineTotal_arr = []

            for i in range(1, boxes+1):
                name_arr.append(request.form.get("bread_"+str(i)))
                qtySold_arr.append(request.form.get("qtySold_"+str(i)))
                lineTotal_arr.append(round(float(request.form.get("lineTotal_"+str(i))), 2))
            

            ### Update Sale
            query = "UPDATE sales SET customerID = %s, saleTotal = %s WHERE saleID = %s;"
            cur = mysql.connection.cursor()
            cur.execute(query, (customerID, sum(lineTotal_arr), saleID))
            mysql.connection.commit()

            ### Get Incrementer for soldProductsID
            query = f"SELECT min(soldProductID) from soldProducts WHERE saleID = { saleID };"
            soldProductID = execute_query_dict(query=query).fetchall()
            soldProductID = soldProductID[0]['min(soldProductID)']
            
            ### Update soldProducts
            for i in range(1, boxes+1):
                query = "UPDATE soldProducts SET productID = %s, qtySold = %s, lineTotal = %s WHERE saleID = %s and soldProductID = %s;"
                cur = mysql.connection.cursor()
                #productID = db.execute_query_dict(db_connection=db_connection, query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" )
                #productID = productID.fetchall()[0]['productID']  # [{:}] list of dictionaries format.
                ## name_arr is already in product IDs for this Update Function.
                cur.execute(query, (name_arr[i-1], qtySold_arr[i-1], lineTotal_arr[i-1], saleID, soldProductID))
                mysql.connection.commit()
                soldProductID += 1

            return redirect(url_for('sales'))

    return render_template('sales.html', sales=sales_results, soldProducts=soldProducts_results, customers=customers_results, products= products_results,count=sales_create_count, update_sales_results=update_sales_results, sale_id = int(saleID))


# -- Delete a Sale
@app.route("/delete_sales/<int:saleID>")
def delete_sales(saleID):
    ## Delete from sales
    query = "DELETE FROM sales where saleID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (saleID,))
    mysql.connection.commit()

    return redirect("/sales")


### Cultures ###
# -- Cultures Page
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


# -- Delete a Culture
@app.route("/cultures/<int:culturesID>", methods=["DELETE"])
def deleteCultures(culturesID):

    # Then Delete culture (cultures)
    delete_cultures_query = "DELETE FROM cultures WHERE cultureID=%s;"
    execute_query(query=delete_cultures_query, query_params=(culturesID,))

    response_data = {"message": "Culture successfully deleted"}
    return jsonify(response_data), 200


### Allergens ### 
# -- Allergens Page
@app.route("/allergens", methods=["POST", "GET"])
def allergens():
    if request.method == "GET":
        allergens_query = "SELECT * FROM allergens;"
        allergens_results = execute_query(query=allergens_query)

        allergensProducts_query = "SELECT allergensProducts.allergensProductID, breadProducts.name as 'Bread Product', allergens.name as Allergen FROM allergensProducts LEFT JOIN breadProducts ON breadProducts.productID = allergensProducts.productID LEFT JOIN allergens ON allergensProducts.allergenID = allergens.allergenID Group by allergensProducts.allergensProductID;"
        allergensProducts_results = execute_query(query=allergensProducts_query)

        #Render the template with the allergens
        return render_template('allergens.html', allergens=allergens_results, allergensProducts=allergensProducts_results) 
    
    elif request.method == "POST":
        # Retrieve form data
        name = request.form.get('name')

        # Part of Add Allergen - Adding Allergens to the Intersection Table
        insert_query_allergens = "INSERT INTO allergens (name) VALUES (%s); " 
        allergens_results = execute_query(query=insert_query_allergens, query_params=(name,))

        # Redirect or render a respose
        return redirect('/allergens') # Redirect to the allergens page after processessing the form

# -- Delete an Allergen
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


# Listener
if __name__ == "__main__":

    #Start the app on port 3000, it will be different once hosted
    app.run(port=3000, debug='TRUE')