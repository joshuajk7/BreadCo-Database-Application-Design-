from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request, url_for
import database.db_connector as db_connector
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #last 4 of onid
app.config['MYSQL_DB'] = 'project_sample'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

# Citation: 
db_connection = db_connector.connect_to_database()

## Helper Functions
# -- db_connection is always established beforehand.
def execute_query(query, query_params=()):
    db_connection = db_connector.connect_to_database()
    return db_connector.execute_query(db_connection, query, query_params)

## Routes

# -- Home Page
## Returns User Home
@app.route('/')
def home():
    return render_template('home.html')

# -- Bread Page
@app.route('/bread', methods=['GET', 'POST'])
def bread():
    return render_template('bread.html')

# -- Sales and SoldProducts Page
@app.route('/sales', methods=['GET', 'POST'])
def sales(sales_create_count=1, update_sales_results=0, saleID=0):

    # Display Table Data for Sales and SoldProducts
    query = "SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as 'Sale Total' FROM sales LEFT JOIN customers ON sales.customerID = customers.customerID LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID Group by sales.saleID;"
    sales_results = execute_query(query=query).fetchall()

    query = "SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as 'Product Name',  soldProducts.qtySold, soldProducts.lineTotal FROM soldProducts LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID LEFT JOIN sales on sales.saleID = soldProducts.saleID GROUP by soldProducts.soldProductID;"
    soldProducts_results = execute_query(query).fetchall()

    query = "SELECT customerID, name from customers;"
    customers_results = execute_query(query=query).fetchall()

    query = "SELECT productID, name from breadProducts;"
    products_results = execute_query(query=query).fetchall()
    
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
                saleID = execute_query(query=query).fetchall()
                saleID = saleID[0]['max(saleID)']

                query = "INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal) Values (%s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                productID = execute_query(query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" ).fetchall()
                productID = productID[0]['productID']  # [{:}] list of dictionaries format.
                cur.execute(query, (saleID, productID, qtySold_arr[i-1], lineTotal_arr[i-1]))
                mysql.connection.commit()

            return redirect(url_for('sales'))
        
        # Update a Sale Intro 
        elif request.form.get('saleID'):
            saleID = request.form.get('saleID')
            query = f"SELECT * from soldProducts where saleID = {saleID};"
            update_sales_results = execute_query(query=query)

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
            soldProductID = execute_query(query=query).fetchall()
            soldProductID = soldProductID[0]['min(soldProductID)']
            
            ### Update soldProducts
            for i in range(1, boxes+1):
                query = "UPDATE soldProducts SET productID = %s, qtySold = %s, lineTotal = %s WHERE saleID = %s and soldProductID = %s;"
                cur = mysql.connection.cursor()
                #productID = db.execute_query(db_connection=db_connection, query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" )
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

# -- Customers Page
@app.route("/customers", methods=['GET', 'POST'])
def customers(load=False):
    
    # Display Customers Table
    query = "SELECT customerID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers"
    customers_results = execute_query(query=query).fetchall()

    # Grab series of sales ID to cross refence with Delete (fix dml reflect this query)
    customers_in_sales = []
    query = "SELECT customerID FROM sales;"
    results = execute_query(query=query).fetchall()

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


        # Load a Customer by pressing the Update on Table (implement potentially later?)
        # if customerID != 0:
        #    query = f"SELECT customerID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers WHERE customerID = { customerID };"
        #   load = execute_query(query=query).fetchall()
    
        # Updating a Customer
        # Load a Customer
        if request.form.get('loadCustomer'):
            customerID = int(request.form.get('loadedCustomer'))
            query = f"SELECT customerID, name, email, phoneNumber, streetAddress, city, state, zipCode FROM customers WHERE customerID = { customerID };"
            load = execute_query(query=query).fetchall()

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

# -- Delete a Customer
@app.route("/delete_customers/<int:customerID>")
def delete_customers(customerID):
    ## Delete from customers
    query = "DELETE FROM customers where customerID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (customerID,))
    mysql.connection.commit()

    return redirect("/customers")

@app.route('/cultures', methods=['GET', 'POST'])
def cultures():
    return render_template('cultures.html')

@app.route('/allergens', methods=['GET', 'POST'])
def allergens():
    return render_template('allergens.html')


# Listener
if __name__ == "__main__":

    #Start the app on port 3000, it will be different once hosted
    app.run(port=3000, debug=True)
