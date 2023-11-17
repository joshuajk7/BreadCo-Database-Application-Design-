from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request, url_for
import database.db_connector as db
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #last 4 of onid
app.config['MYSQL_DB'] = 'project_sample'
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

# Citation: 
db_connection = db.connect_to_database()

## Global Variables

## Routes
# -- Home Page
## Returns User Home
@app.route('/')
def home():
    return render_template('home.html')

# -- Bread Page
## Displays Bread Page
@app.route('/bread', methods=['GET', 'POST'])
def bread():
    return render_template('bread.html')

@app.route('/sales', methods=['GET', 'POST'])
def sales(sales_create_count=1, update_sales_results=0, saleID=0):
    # Display Table Data for Sales and SoldProducts
    query = "SELECT sales.saleID, customers.name as Customer, sum(soldProducts.lineTotal) as 'Sale Total' FROM sales LEFT JOIN customers ON sales.customerID = customers.customerID LEFT JOIN soldProducts ON sales.saleID = soldProducts.saleID Group by sales.saleID;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    sales_results = cursor.fetchall()

    query = "SELECT soldProducts.soldProductID, sales.saleID, breadProducts.name as 'Product Name',  soldProducts.qtySold, soldProducts.lineTotal FROM soldProducts LEFT JOIN breadProducts on breadProducts.productID = soldProducts.productID LEFT JOIN sales on sales.saleID = soldProducts.saleID GROUP by soldProducts.soldProductID;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    soldProducts_results = cursor.fetchall()

    query = "SELECT customerID, name from customers;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    customers_results = cursor.fetchall()

    query = "SELECT productID, name from breadProducts;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    products_results = cursor.fetchall()
    
    if request.method == 'POST':
        # Add a Sale Feature
        ## Add and Remove Product from Add Sale
        if request.form.get('soldProduct'):
            sales_create_count=int(request.form['soldProduct'])
        elif request.form.get('removeProduct'):
            sales_create_count=int(request.form['removeProduct'])
        elif request.form.get('submitSale'):
            sales_create_count=int(request.form['submitSale'])

        if request.form.get('submitSale'):
            ### Gather Add Data, put all data in array. Check for Discrepancies.
            sales_create_count=int(request.form['submitSale'])
            saleID = int(request.form.get('getSaleID'))
            customer = int(request.form['customer']) ## Trying to convert as INT
            name_arr = []
            qtySold_arr = []
            lineTotal_arr = []
            return saleID

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
                query = "INSERT INTO soldProducts(saleID, productID, qtySold, lineTotal) Values (%s, %s, %s, %s);"
                cur = mysql.connection.cursor()
                productID = db.execute_query(db_connection=db_connection, query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" )
                productID = productID.fetchall()[0]['productID']  # [{:}] list of dictionaries format.
                cur.execute(query, (saleID, productID, qtySold_arr[i-1], lineTotal_arr[i-1]))
                mysql.connection.commit()

                # Testing
                #q = f"Select productID from breadProducts where name = '{name_arr[i-1]}';"
                #cursor = db.execute_query(db_connection=db_connection, query=q)
                #testing.append(cursor.fetchall())
                #testing.append(int(cur.execute(f"(select productID from breadProducts where name = '{name_arr[i-1]}')"))) 
                #cur = mysql.connection.cursor()
                #query = f"(select productID from breadProducts where name = '{name_arr[i-1]}')"
                #cursor = db.execute_query(db_connection=db_connection, query=query)

            return redirect(url_for('sales'))
        
        # Update a Sale Intro 
        elif request.form.get('saleID'):
            saleID = request.form.get('saleID')
            query = f"SELECT * from soldProducts where saleID = {saleID};"
            cursor = db.execute_query(db_connection=db_connection, query=query)
            update_sales_results = cursor.fetchall()
        # Gather Information to Update
        else:
            boxes = int(request.form.get('updateLength'))
            saleID = int(request.form.get('updateSale'))
            customer = request.form.get('customer')
            name_arr = []
            qtySold_arr = []
            lineTotal_arr = []
            # error here, because there is no length of this parttion?

            for i in range(1, boxes+1):
                name_arr.append(request.form.get("bread_"+str(i)))
                qtySold_arr.append(request.form.get("qtySold_"+str(i)))
                lineTotal_arr.append(round(float(request.form.get("lineTotal_"+str(i))), 2))

            ### Update Sale
            query = "UPDATE sales SET customerID = %s, saleTotal = %s WHERE saleID = %s;"
            cur = mysql.connection.cursor()
            cur.execute(query, (customer, sum(lineTotal_arr), saleID))
            mysql.connection.commit()
            
            ### Add into soldProducts
            for i in range(1, boxes+1):
                query = "UPDATE soldProducts SET saleID = %s, productID = %s, qtySold = %s, lineTotal = %s;"
                cur = mysql.connection.cursor()
                #productID = db.execute_query(db_connection=db_connection, query = f"Select productID from breadProducts where name = '{name_arr[i-1]}';" )
                #productID = productID.fetchall()[0]['productID']  # [{:}] list of dictionaries format.
                ## name_arr is already in product IDs for this Update Function.
                cur.execute(query, (saleID, name_arr[i-1], qtySold_arr[i-1], lineTotal_arr[i-1]))
                mysql.connection.commit()
            
            return redirect(url_for('sales'))

    return render_template('sales.html', sales=sales_results, soldProducts=soldProducts_results, customers=customers_results, products= products_results,count=sales_create_count, update_sales_results=update_sales_results, sale_id = int(saleID))


@app.route("/delete_sales/<int:saleID>")
def delete_sales(saleID):
    ## Delete from Sale
    query = "DELETE FROM sales where saleID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (saleID,))
    mysql.connection.commit()

    return redirect("/sales")

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    return render_template('customers.html')

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