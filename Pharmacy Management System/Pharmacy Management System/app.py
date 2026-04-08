
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
import mysql.connector
from datetime import datetime, timedelta,date
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error,connect
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.secret_key = '123'  # For flash messages and session management


import mysql.connector
from mysql.connector import pooling, Error

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "PharmacyManagement",
    "connection_timeout": 300,  
    "pool_name": "mypool",
    "pool_size": 5,
    "pool_reset_session": True  
}

try:
    db_pool = pooling.MySQLConnectionPool(**db_config)
except Error as e:
    print(f"Error setting up connection pool: {e}")
    db_pool = None

def get_db_connection():
    if db_pool is None:
        raise Error("Connection pool is not initialized")
    try:
        conn = db_pool.get_connection()
        if not conn.is_connected():
            conn.reconnect()
        return conn
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

def ensure_connection(conn):
    if conn is None:
        return get_db_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=5)
        return conn
    except Error as e:
        print(f"Error pinging database: {e}")
        try:
            conn = get_db_connection()
            return conn
        except Error as e:
            print(f"Error reconnecting to database: {e}")
            return None

########################################################################
##login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error='Username and password are required')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT * 
                FROM Pharmacist 
                WHERE Username = %s AND Password = %s
            """
            cursor.execute(query, (username, password))
            pharmacist = cursor.fetchone()

            if pharmacist:
                session['pharmacist_id'] = pharmacist['Pharmacist_ID']
                session['Role'] = pharmacist['Role']
                session['pharmacist_name'] = pharmacist['Name']
                if pharmacist['Role'] == 'Senior Pharmacist':
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('dashboard2.html', name=session['pharmacist_name'])
            else:
                return render_template('login.html', error='Invalid username or password')

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return render_template('login.html', error='Database error occurred')

        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    return render_template('login.html')

########################################################################
##dashboard
@app.route('/dashboard')
def dashboard():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM Customer")
        total_customers = cursor.fetchone()[0]

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        total_customers = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Pharmacist WHERE Role = 'Pharmacist'")
        total_pharmacist = cursor.fetchone()[0]

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        total_pharmacist = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT SUM(op.Quantity * op.Unit_Price) AS TotalRevenue
            FROM Orders o
            JOIN Order_Product op ON o.Order_ID = op.Order_ID
            WHERE o.Order_Date = %s
        """
        cursor.execute(query, (current_date,))
        TotalRevenue = cursor.fetchone()[0] or 0

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        TotalRevenue = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT SUM(Price * Quantity) AS TotalStockValue FROM Product")
        TotalStockValue = cursor.fetchone()[0]

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        TotalStockValue = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT SUM(op.Quantity) AS TotalQuantitySold
            FROM Orders o
            JOIN Order_Product op ON o.Order_ID = op.Order_ID
            WHERE o.Order_Date = %s
        """
        cursor.execute(query, (current_date,))
        Quantity_of_sales = cursor.fetchone()[0] or 0

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        Quantity_of_sales = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            WITH Revenue AS (
                SELECT SUM(op.Quantity * op.Unit_Price) AS TotalRevenue
                FROM Orders o
                JOIN Order_Product op ON o.Order_ID = op.Order_ID
                WHERE DATE(o.Order_Date) = %s
            ),
            Cost AS (
                SELECT SUM(po.Quantity * po.Unit_Cost) AS TotalCost
                FROM Purchase_Order po
                WHERE DATE(po.Purchase_Date) = %s
            )
            SELECT COALESCE(r.TotalRevenue, 0) - COALESCE(c.TotalCost, 0) AS Profit
            FROM Revenue r
            CROSS JOIN Cost c
        """
        cursor.execute(query, (current_date, current_date))
        TotalRevenueInDay = cursor.fetchone()[0] or 0

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        TotalRevenueInDay = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT p.Name, po.Quantity, (po.Quantity * po.Unit_Cost) AS TotalPrice
            FROM Purchase_Order po
            JOIN Product p ON po.Product_ID = p.Product_ID
            WHERE po.Purchase_Date = %s
        """
        cursor.execute(query, (current_date,))
        orders = cursor.fetchall()

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        orders = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT p.Name AS pharmacist_name, c.Name AS customer_name,
                   SUM(op.Quantity * op.Unit_Price) AS total_price, o.Payment_Method
            FROM Customer c
            JOIN Orders o ON c.Customer_ID = o.Customer_ID
            JOIN Order_Product op ON o.Order_ID = op.Order_ID
            JOIN Pharmacist p ON p.Pharmacist_ID = o.Pharmacist_ID
            WHERE o.Order_Date = %s
            GROUP BY p.Name, c.Name, o.Payment_Method
        """
        cursor.execute(query, (current_date,))
        sales = cursor.fetchall()

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sales = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT COUNT(*) FROM Subscription
            WHERE End_Date >= %s
        """
        cursor.execute(query, (current_date,))
        NumberOfSubscribers = cursor.fetchone()[0] or 0

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        NumberOfSubscribers = "Error fetching data"

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = """
            SELECT SUM(po.Quantity * po.Unit_Cost) AS TotalOrderPrice
            FROM Purchase_Order po
            WHERE po.Purchase_Date = %s
        """
        cursor.execute(query, (current_date,))
        TotalOrderPrice = cursor.fetchone()[0] or 0

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        TotalOrderPrice = "Error fetching data"

    return render_template('dashboard.html', sales=sales, orders=orders, NumberOfSubscribers=NumberOfSubscribers,
                           TotalOrderPrice=TotalOrderPrice, TotalStockValue=TotalStockValue,
                           total_customers=total_customers, total_pharmacist=total_pharmacist,
                           Quantity_of_sales=Quantity_of_sales, TotalRevenue=TotalRevenue,
                           TotalRevenueInDay=TotalRevenueInDay)


########################################################################
##product
@app.route('/medicien', methods=['GET'])
def medicien():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    search_query = request.args.get('search', default='', type=str)

    if search_query.isdigit():
        cursor.execute("SELECT * FROM Product WHERE Product_ID = %s", (search_query,))
    elif search_query:
        cursor.execute("SELECT * FROM Product WHERE Name LIKE %s ORDER BY Quantity", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT * FROM Product ORDER BY Quantity")

    rows = cursor.fetchall()

    cursor.execute("SELECT Name FROM Product WHERE Quantity <= 5")
    low_stock_products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('medicen.html', rows=rows, low_stock_products=low_stock_products)

@app.route('/medicien2', methods=['GET'])
def medicien2():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    search_query = request.args.get('search', default='', type=str)

    if search_query.isdigit():
        cursor.execute("SELECT * FROM Product WHERE Product_ID = %s", (search_query,))
    elif search_query:
        cursor.execute("SELECT * FROM Product WHERE Name LIKE %s ORDER BY Quantity", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT * FROM Product ORDER BY Quantity")

    rows = cursor.fetchall()

    cursor.execute("SELECT Name FROM Product WHERE Quantity <= 5")
    low_stock_products = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('medicen2.html', rows=rows, low_stock_products=low_stock_products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['Price']
        expiration_date = request.form['ExpirationDate']
        product_type = request.form['ProductType']
        description = request.form['Description']
        quantity = request.form['Quantity']
        last_updated_date = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Product (Name, Price, Expiration_Date, Type, Description,Quantity, LastUpdatedDate) VALUES (%s, %s, %s, %s, %s, %s,%s)',
                       (name, price, expiration_date, product_type, description,quantity, last_updated_date))
        conn.commit()
        conn.close()

        return redirect(url_for('medicien'))
    return render_template('add_product.html')

@app.route('/add2', methods=['GET', 'POST'])
def add_product2():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['Price']
        expiration_date = request.form['ExpirationDate']
        product_type = request.form['ProductType']
        description = request.form['Description']
        quantity = request.form['Quantity']
        last_updated_date = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Product (Name, Price, Expiration_Date, Type, Description,Quantity, LastUpdatedDate) VALUES (%s, %s, %s, %s, %s, %s,%s)',
                       (name, price, expiration_date, product_type, description,quantity, last_updated_date))
        conn.commit()
        conn.close()

        return redirect(url_for('medicien2'))
    return render_template('add_product2.html')

@app.route('/edit_product/<string:name>', methods=['GET', 'POST'])
def edit_product(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching product with name: {name}")
    cursor.execute('SELECT * FROM Product WHERE Name = %s', (name,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        print("Product not found!")
        return redirect(url_for('medicien'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['name']
        price = request.form['Price']
        expiration_date = request.form['ExpirationDate']
        product_type = request.form['ProductType']
        description = request.form['Description']
        last_updated_date = datetime.now().strftime("%Y-%m-%d")
        quantity = request.form['Quantity']
        cursor.execute('''
            UPDATE Product 
            SET Name = %s, Price = %s, Type = %s, Expiration_Date = %s, LastUpdatedDate = %s, Description = %s, Quantity = %s
            WHERE Name = %s
        ''', (new_name, price, product_type, expiration_date, last_updated_date, description, quantity, name))
        conn.commit()
        conn.close()
        print("Product updated successfully!")
        return redirect(url_for('medicien'))

    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/edit_product2/<string:name>', methods=['GET', 'POST'])
def edit_product2(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching product with name: {name}")
    cursor.execute('SELECT * FROM Product WHERE Name = %s', (name,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        print("Product not found!")
        return redirect(url_for('medicien2'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['name']
        price = request.form['Price']
        expiration_date = request.form['ExpirationDate']
        product_type = request.form['ProductType']
        description = request.form['Description']
        last_updated_date = datetime.now().strftime("%Y-%m-%d")
        quantity = request.form['Quantity']
        cursor.execute('''
            UPDATE Product 
            SET Name = %s, Price = %s, Type = %s, Expiration_Date = %s, LastUpdatedDate = %s, Description = %s, Quantity = %s
            WHERE Name = %s
        ''', (new_name, price, product_type, expiration_date, last_updated_date, description, quantity, name))
        conn.commit()
        conn.close()
        print("Product updated successfully!")
        return redirect(url_for('medicien2'))

    conn.close()
    return render_template('edit_product2.html', product=product)

@app.route('/delete_product/<string:name>', methods=['GET', 'POST'])
def delete_product(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Product WHERE Name = %s', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('medicien'))

@app.route('/delete_product2/<string:name>', methods=['GET', 'POST'])
def delete_product2(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Product WHERE Name = %s', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('medicien2'))


########################################################################
##pharmacist
@app.route("/users", methods=['GET'])
def users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    search_query = request.args.get('search', default='', type=str)

    if search_query.isdigit():
        cursor.execute("SELECT * FROM Pharmacist WHERE Pharmacist_ID = %s", (search_query,))
    elif search_query:
        cursor.execute("SELECT * FROM Pharmacist WHERE Name LIKE %s", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT Name, Contact_Info, Role, Wage, Working_Hours FROM Pharmacist")

    rows = cursor.fetchall()

    first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    query = """
        SELECT p.Name, COUNT(o.Order_ID) AS TotalSales
        FROM Pharmacist p
        JOIN Orders o ON p.Pharmacist_ID = o.Pharmacist_ID
        WHERE o.Order_Date >= %s
        GROUP BY p.Pharmacist_ID, p.Name
        ORDER BY TotalSales DESC
        LIMIT 1
    """
    cursor.execute(query, (first_day_of_month,))
    topUser = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('users.html', rows=rows, topUser=topUser)

@app.route("/users2", methods=['GET'])
def users2():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """SELECT * FROM Pharmacist WHERE Pharmacist_ID = %s"""
    pharmacist_id = session['pharmacist_id']
    cursor.execute(query, (pharmacist_id,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('users2.html', rows=rows)

@app.route('/addusers', methods=['GET', 'POST'])
def add_users():
    if request.method == 'POST':
        name = request.form['Name']
        contact_info = request.form['ContactInfo']
        role = request.form['Role']
        username = request.form['Username']
        password = request.form['Password']
        wage = request.form['Wage']
        Working_Hours = request.form['Working_Houres']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Pharmacist (Name, Contact_Info, Role, Username, Password, Wage, Working_Hours) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (name, contact_info, role, username, password, wage, Working_Hours))
        conn.commit()
        conn.close()
        return redirect(url_for('users'))
    return render_template('add_users.html')

@app.route('/edit_users/<string:name>', methods=['GET', 'POST'])
def edit_users(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching user with Name: {name}")
    cursor.execute('SELECT * FROM Pharmacist WHERE Name = %s', (name,))
    users = cursor.fetchone()

    if not users:
        conn.close()
        print("User not found!")
        return redirect(url_for('users'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['name']
        contact_info = request.form['Contact_Info']
        role = request.form['Role']
        username = request.form['Username']
        password = request.form['Password']
        wage = request.form['Wage']
        workinghours = request.form['Working_Hours']

        cursor.execute('''
            UPDATE Pharmacist 
            SET Name = %s, Contact_Info = %s, Role = %s, Wage = %s,Working_Hours =%s,Username=%s,Password=%s
            WHERE Name = %s
        ''', (new_name, contact_info, role, wage,workinghours,username,password,name))
        conn.commit()
        conn.close()
        print("User updated successfully!")
        return redirect(url_for('users'))

    conn.close()
    return render_template('edit_users.html', users=users)

@app.route('/edit_users2/<string:name>', methods=['GET', 'POST'])
def edit_users2(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching user with Name: {name}")
    cursor.execute('SELECT * FROM Pharmacist WHERE Name = %s', (name,))
    users = cursor.fetchone()

    if not users:
        conn.close()
        print("User not found!")
        return redirect(url_for('users2'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['name']
        contact_info = request.form['Contact_Info']
        role = request.form['Role']
        username = request.form['Username']
        password = request.form['Password']
        wage = request.form['Wage']
        workinghours = request.form['Working_Hours']
        cursor.execute('''
            UPDATE Pharmacist 
            SET Name = %s, Contact_Info = %s, Role = %s, Wage = %s,Working_Hours =%s,Username=%s,Password=%s
            WHERE Name = %s
        ''', (new_name, contact_info, role, wage,workinghours,username,password,name))
        conn.commit()
        conn.close()
        print("User updated successfully!")
        return redirect(url_for('users2'))

    conn.close()
    return render_template('edit_users2.html', users=users)

@app.route('/delete_users/<string:name>', methods=['GET', 'POST'])
def delete_users(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Pharmacist WHERE Name = %s', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))


########################################################################
##customers
@app.route('/customer', methods=['GET'])
def customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_query = request.args.get('search', default='', type=str)

    if search_query.isdigit():
        cursor.execute("SELECT * FROM Customer WHERE Customer_ID = %s", (search_query,))
    elif search_query:
        cursor.execute("SELECT * FROM Customer WHERE Name LIKE %s", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT Name, City, Street, DateOfBirth, Email, PhoneNumber FROM Customer")

    rows = cursor.fetchall()

    first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    query = """
        SELECT c.Name, COUNT(o.Order_ID) AS TotalSales
        FROM Customer c
        JOIN Orders o ON c.Customer_ID = o.Customer_ID
        WHERE o.Order_Date >= %s
        GROUP BY c.Customer_ID, c.Name
        ORDER BY TotalSales DESC
        LIMIT 1
    """
    cursor.execute(query, (first_day_of_month,))
    topCustomer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('customers.html', rows=rows, topCustomer=topCustomer)

@app.route('/customer2', methods=['GET'])
def customers2():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_query = request.args.get('search', default='', type=str)

    if search_query.isdigit():
        cursor.execute("SELECT * FROM Customer WHERE Customer_ID = %s", (search_query,))
    elif search_query:
        cursor.execute("SELECT * FROM Customer WHERE Name LIKE %s", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT Name, City, Street, DateOfBirth, Email, PhoneNumber FROM Customer")

    rows = cursor.fetchall()

    first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    query = """
        SELECT c.Name, COUNT(o.Order_ID) AS TotalSales
        FROM Customer c
        JOIN Orders o ON c.Customer_ID = o.Customer_ID
        WHERE o.Order_Date >= %s
        GROUP BY c.Customer_ID, c.Name
        ORDER BY TotalSales DESC
        LIMIT 1
    """
    cursor.execute(query, (first_day_of_month,))
    topCustomer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('customers2.html', rows=rows, topCustomer=topCustomer)

@app.route('/add_customers', methods=['GET', 'POST'])
def add_customers():
    if request.method == 'POST':
        name = request.form['Name']
        city = request.form['City']
        street = request.form['Street']
        date_of_birth = request.form['DateOfBirth']
        email = request.form['Email']
        phone = request.form['PhoneNumber']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Customer (Name, City, Street, DateOfBirth, Email, PhoneNumber) VALUES (%s, %s, %s, %s, %s, %s)',
                       (name, city, street, date_of_birth, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/add_customers2', methods=['GET', 'POST'])
def add_customers2():
    if request.method == 'POST':
        name = request.form['Name']
        city = request.form['City']
        street = request.form['Street']
        date_of_birth = request.form['DateOfBirth']
        email = request.form['Email']
        phone = request.form['PhoneNumber']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Customer (Name, City, Street, DateOfBirth, Email, PhoneNumber) VALUES (%s, %s, %s, %s, %s, %s)',
                       (name, city, street, date_of_birth, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('customers2'))
    return render_template('add_customer2.html')

@app.route('/edit_customers/<string:name>', methods=['GET', 'POST'])
def edit_customers(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching Customer with Name: {name}")
    cursor.execute('SELECT * FROM Customer WHERE Name = %s', (name,))
    customers = cursor.fetchone()

    if not customers:
        conn.close()
        print("Customer not found!")
        return redirect(url_for('customers'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['Name']
        city = request.form['City']
        street = request.form['Street']
        date_of_birth = request.form['DateOfBirth']
        email = request.form['Email']
        phone = request.form['PhoneNumber']
        cursor.execute('''
            UPDATE Customer 
            SET Name = %s, City = %s, Street = %s, DateOfBirth = %s, Email = %s, PhoneNumber = %s
            WHERE Name = %s
        ''', (new_name, city, street, date_of_birth, email, phone, name))
        conn.commit()
        conn.close()
        print("Customer updated successfully!")
        return redirect(url_for('customers'))

    conn.close()
    return render_template('edit_customers.html', customers=customers)

@app.route('/edit_customers2/<string:name>', methods=['GET', 'POST'])
def edit_customers2(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching Customer with Name: {name}")
    cursor.execute('SELECT * FROM Customer WHERE Name = %s', (name,))
    customers = cursor.fetchone()

    if not customers:
        conn.close()
        print("Customer not found!")
        return redirect(url_for('customers2'))

    if request.method == 'POST':
        print("Form submitted!")
        new_name = request.form['Name']
        city = request.form['City']
        street = request.form['Street']
        date_of_birth = request.form['DateOfBirth']
        email = request.form['Email']
        phone = request.form['PhoneNumber']
        cursor.execute('''
            UPDATE Customer 
            SET Name = %s, City = %s, Street = %s, DateOfBirth = %s, Email = %s, PhoneNumber = %s
            WHERE Name = %s
        ''', (new_name, city, street, date_of_birth, email, phone, name))
        conn.commit()
        conn.close()
        print("Customer updated successfully!")
        return redirect(url_for('customers2'))

    conn.close()
    return render_template('edit_customers2.html', customers=customers)

@app.route('/delete_customers/<string:name>', methods=['GET', 'POST'])
def delete_customers(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Customer WHERE Name = %s', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

@app.route('/delete_customers2/<string:name>', methods=['GET', 'POST'])
def delete_customers2(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Customer WHERE Name = %s', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('customers2'))


########################################################################
##Purchase_Order
@app.route('/orders', methods=['GET'])
def orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_query = request.args.get('search', default='', type=str)

    try:
        if search_query.isdigit():
            query = """
                SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                       po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                FROM Purchase_Order po
                JOIN Product p ON po.Product_ID = p.Product_ID
                JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                WHERE po.Purchase_ID = %s
                ORDER BY po.Purchase_Date DESC
            """
            cursor.execute(query, (search_query,))
        elif search_query:
            try:
                datetime.strptime(search_query, '%Y-%m-%d')
                query = """
                    SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                    FROM Purchase_Order po
                    JOIN Product p ON po.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                    WHERE po.Purchase_Date = %s
                    ORDER BY po.Purchase_Date DESC
                """
                cursor.execute(query, (search_query,))
            except ValueError:
                cursor.close()
                conn.close()
                return "Invalid date format. Please use YYYY-MM-DD.", 400
        else:
            query = '''
                SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                       po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                FROM Purchase_Order po
                JOIN Product p ON po.Product_ID = p.Product_ID
                JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                ORDER BY po.Purchase_Date DESC
            '''
            cursor.execute(query)

        rows = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        return f"Database error: {str(e)}", 400

    cursor.close()
    conn.close()
    return render_template('order.html', rows=rows)

@app.route('/orders2', methods=['GET'])
def orders2():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_query = request.args.get('search', default='', type=str)

    try:
        if search_query.isdigit():
            query = """
                SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                       po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                FROM Purchase_Order po
                JOIN Product p ON po.Product_ID = p.Product_ID
                JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                WHERE po.Purchase_ID = %s
                ORDER BY po.Purchase_Date DESC
            """
            cursor.execute(query, (search_query,))
        elif search_query:
            try:
                datetime.strptime(search_query, '%Y-%m-%d')
                query = """
                    SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                    FROM Purchase_Order po
                    JOIN Product p ON po.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                    WHERE po.Purchase_Date = %s
                    ORDER BY po.Purchase_Date DESC
                """
                cursor.execute(query, (search_query,))
            except ValueError:
                cursor.close()
                conn.close()
                return "Invalid date format. Please use YYYY-MM-DD.", 400
        else:
            query = '''
                SELECT po.Purchase_ID AS OrderID, ph.Name AS PharmsticName, p.Name AS ProductName,
                       po.Purchase_Date AS OrderDate, po.Quantity, po.Supplier_Name, po.Unit_Cost
                FROM Purchase_Order po
                JOIN Product p ON po.Product_ID = p.Product_ID
                JOIN Pharmacist ph ON po.Pharmacist_ID = ph.Pharmacist_ID
                ORDER BY po.Purchase_Date DESC
            '''
            cursor.execute(query)

        rows = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        return f"Database error: {str(e)}", 400

    cursor.close()
    conn.close()
    return render_template('order2.html', rows=rows)


@app.route('/add_orders', methods=['GET', 'POST'])
def add_orders():
    if request.method == 'POST':
        if 'pharmacist_id' not in session:
            return redirect(url_for('login'))

        pharmacist_id = session['pharmacist_id']
        product_ids = request.form.getlist('ProductID[]')
        supplier_names = request.form.getlist('Supplier_Name[]')
        quantities = request.form.getlist('Quantity[]')

        if len(product_ids) != len(supplier_names) or len(product_ids) != len(quantities) or not product_ids:
            return "All fields must be filled for each product.", 400

        purchase_date = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for i in range(len(product_ids)):
                product_id = product_ids[i].strip()
                supplier_name = supplier_names[i].strip() or None
                quantity_str = quantities[i].strip()

                if not product_id or not quantity_str:
                    return f"Missing data for product {i+1}.", 400
                if not product_id.isdigit() or not quantity_str.isdigit():
                    return f"Invalid Product ID or Quantity for product {i+1}.", 400

                quantity = int(quantity_str)
                if quantity < 1:
                    return f"Quantity must be 1 or more for product {i+1}.", 400

                cursor.execute('SELECT Price FROM Product WHERE Product_ID = %s', (product_id,))
                result = cursor.fetchone()
                if not result:
                    return f"Product ID {product_id} not found.", 400
                unit_cost = result[0]
                cursor.execute('''
                    INSERT INTO Purchase_Order (Pharmacist_ID, Product_ID, Supplier_Name, Purchase_Date, Quantity, Unit_Cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (pharmacist_id, product_id, supplier_name, purchase_date, quantity, unit_cost))
                cursor.execute('''
                    UPDATE Product 
                    SET Quantity = Quantity + %s
                    WHERE Product_ID = %s
                ''', (quantity, product_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"Database error: {str(e)}", 400
        finally:
            conn.close()

        return redirect(url_for('orders'))
    
    return render_template('add_order.html')

@app.route('/add_orders2', methods=['GET', 'POST'])
def add_orders2():
    if request.method == 'POST':
        if 'pharmacist_id' not in session:
            return redirect(url_for('login'))

        pharmacist_id = session['pharmacist_id']
        product_ids = request.form.getlist('ProductID[]')
        supplier_names = request.form.getlist('Supplier_Name[]')
        quantities = request.form.getlist('Quantity[]')

        if len(product_ids) != len(supplier_names) or len(product_ids) != len(quantities) or not product_ids:
            return "All fields must be filled for each product.", 400

        purchase_date = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for i in range(len(product_ids)):
                product_id = product_ids[i].strip()
                supplier_name = supplier_names[i].strip() or None
                quantity_str = quantities[i].strip()

                if not product_id or not quantity_str:
                    return f"Missing data for product {i+1}.", 400
                if not product_id.isdigit() or not quantity_str.isdigit():
                    return f"Invalid Product ID or Quantity for product {i+1}.", 400

                quantity = int(quantity_str)
                if quantity < 1:
                    return f"Quantity must be 1 or more for product {i+1}.", 400

                cursor.execute('SELECT Price FROM Product WHERE Product_ID = %s', (product_id,))
                result = cursor.fetchone()
                if not result:
                    return f"Product ID {product_id} not found.", 400
                unit_cost = result[0]

                cursor.execute('''
                    INSERT INTO Purchase_Order (Pharmacist_ID, Product_ID, Supplier_Name, Purchase_Date, Quantity, Unit_Cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (pharmacist_id, product_id, supplier_name, purchase_date, quantity, unit_cost))

                cursor.execute('''
                    UPDATE Product 
                    SET Quantity = Quantity + %s
                    WHERE Product_ID = %s
                ''', (quantity, product_id))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return f"Database error: {str(e)}", 400
        finally:
            conn.close()

        return redirect(url_for('orders2'))

    return render_template('add_order2.html')


@app.route('/edit_orders/<int:id>', methods=['GET', 'POST'])
def edit_orders(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching purchase order with ID: {id}")
    cursor.execute('SELECT * FROM Purchase_Order WHERE Purchase_ID = %s', (id,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        print("Order not found!")
        return redirect(url_for('orders'))

    if request.method == 'POST':
        print("Form submitted!")
        pharmacist_id = session['pharmacist_id']
        product_id = request.form['ProductID']
        supplier_name = request.form['SupplierName']
        quantity = request.form['Quantity']

        try:
            cursor.execute('''
                UPDATE Purchase_Order 
                SET Pharmacist_ID = %s, Product_ID = %s, Supplier_Name = %s, Quantity = %s
                WHERE Purchase_ID = %s
            ''', (pharmacist_id, product_id, supplier_name, quantity, id))
            conn.commit()
            print("Order updated successfully!")
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            return f"Database error: {str(e)}", 400
        finally:
            conn.close()
            return redirect(url_for('orders'))

    conn.close()
    return render_template('edit_order.html', orders=order)

@app.route('/edit_orders2/<int:id>', methods=['GET', 'POST'])
def edit_orders2(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    print(f"Fetching purchase order with ID: {id}")
    cursor.execute('SELECT * FROM Purchase_Order WHERE Purchase_ID = %s', (id,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        print("Order not found!")
        return redirect(url_for('orders2'))

    if request.method == 'POST':
        print("Form submitted!")
        pharmacist_id = session['pharmacist_id']
        product_id = request.form['ProductID']
        supplier_name = request.form['SupplierName']
        quantity = request.form['Quantity']

        try:
            cursor.execute('''
                UPDATE Purchase_Order 
                SET Pharmacist_ID = %s, Product_ID = %s, Supplier_Name = %s, Quantity = %s
                WHERE Purchase_ID = %s
            ''', (pharmacist_id, product_id, supplier_name, quantity, id))
            conn.commit()
            print("Order updated successfully!")
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            return f"Database error: {str(e)}", 400
        finally:
            conn.close()
            return redirect(url_for('orders2'))

    conn.close()
    return render_template('edit_order2.html', orders=order)


@app.route('/delete_orders/<int:id>', methods=['GET', 'POST'])
def delete_orders(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Purchase_Order WHERE Purchase_ID = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

@app.route('/delete_orders2/<int:id>', methods=['GET', 'POST'])
def delete_orders2(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Purchase_Order WHERE Purchase_ID = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders2'))

#####################



########################################################################
##Customer order

@app.route('/sales')
def sales():
    return render_template('index.html')

@app.route('/sales2')
def sales2():
    return render_template('index2.html')

@app.route('/new_sale')
def new_sale():
    today = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed.")

    cursor = None
    try:
        conn = ensure_connection(conn)
        if not conn:
            return render_template('error.html', message="Could not connect to database.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT Prescription_ID, Doctor_Name, Date FROM Prescription')
        prescriptions = cursor.fetchall()
        cursor.execute('SELECT Subscription_ID, Customer_ID, Product_ID FROM Subscription')
        subscriptions = cursor.fetchall()
        cursor.execute('SELECT Product_ID, Name FROM Product')
        products = cursor.fetchall()
        return render_template('new_sale.html', prescriptions=prescriptions, subscriptions=subscriptions, today=today, products=products)

    except Error as e:
        print(f"Error in new_sale: {e}")
        return render_template('error.html', message=f"Error fetching data: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/new_sale2')
def new_sale2():
    today = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Database connection failed.")

    cursor = None
    try:
        conn = ensure_connection(conn)
        if not conn:
            return render_template('error.html', message="Could not connect to database.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT Prescription_ID, Doctor_Name, Date FROM Prescription')
        prescriptions = cursor.fetchall()
        cursor.execute('SELECT Subscription_ID, Customer_ID, Product_ID FROM Subscription')
        subscriptions = cursor.fetchall()
        cursor.execute('SELECT Product_ID, Name FROM Product')
        products = cursor.fetchall()
        return render_template('new_sale2.html', prescriptions=prescriptions, subscriptions=subscriptions, today=today, products=products)

    except Error as e:
        print(f"Error in new_sale2: {e}")
        return render_template('error.html', message=f"Error fetching data: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/submit', methods=['POST'])
def submit_sales():
    if 'pharmacist_id' not in session:
        return redirect(url_for('login'))

    pharmacist_id = int(session['pharmacist_id'])
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('new_sale'))

    cur = conn.cursor(dictionary=True)

    try:
        customer_id = int(request.form["CustomerID"])
        payment_method = request.form.get("payment_method", None)
        insurance_discount = Decimal(request.form.get("insurance_discount", "0") or "0")
        order_date = date.today()
        total_amount = Decimal("0.00")

        # Insert initial order with placeholder total
        cur.execute("""
            INSERT INTO Orders (Customer_ID, Pharmacist_ID, Order_Date, Payment_Method, Total_Amount, Insurance_Discount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, pharmacist_id, order_date, payment_method, total_amount, insurance_discount))
        conn.commit()
        order_id = cur.lastrowid

        # Initialize product list
        product_ids = []
        quantities = []

        # Handle prescription if provided
        prescription_id = request.form.get("PrescriptionID") or None
        doctor_name = request.form.get("DoctorName")
        prescription_date = request.form.get("Date")
        notes = request.form.get("Notes")
        prescription_product_ids = request.form.getlist("PrescriptionProductID[]")
        dosages = request.form.getlist("Dosage[]")
        taken_times = request.form.getlist("TakenTimes[]")
        durations = request.form.getlist("Duration[]")
        prescription_quantities = request.form.getlist("PrescriptionQuantity[]")

        if doctor_name and prescription_date and not prescription_id:
            cur.execute("INSERT INTO Prescription (Customer_ID, Doctor_Name, Date, Notes) VALUES (%s, %s, %s, %s)", 
                       (customer_id, doctor_name, prescription_date, notes))
            prescription_id = cur.lastrowid
            for i in range(len(prescription_product_ids)):
                product_id = prescription_product_ids[i].strip()
                if product_id:
                    cur.execute("INSERT INTO Prescription_Product (Prescription_ID, Product_ID, Dosage, TakenTimes, Duration, Quantity) VALUES (%s, %s, %s, %s, %s, %s)", 
                               (prescription_id, product_id, dosages[i].strip() or None, taken_times[i].strip() or None, durations[i].strip() or None, prescription_quantities[i].strip() or None))
                    product_ids.append(product_id)
                    quantities.append(prescription_quantities[i].strip() or "1")

        # If a prescription is selected, fetch its products
        if prescription_id and not doctor_name:
            cur.execute("SELECT Product_ID, Quantity FROM Prescription_Product WHERE Prescription_ID = %s", (prescription_id,))
            prescription_products = cur.fetchall()
            for product in prescription_products:
                product_ids.append(str(product["Product_ID"]))
                quantities.append(str(product["Quantity"]))

        # Handle subscription if provided
        subscription_id = request.form.get("SubscriptionID") or None
        subscription_product_id = request.form.get("SubscriptionProductID")
        start_date = request.form.get("StartDate")
        end_date = request.form.get("EndDate")
        refill_interval = request.form.get("RefillInterval")

        if subscription_product_id and start_date and refill_interval and not subscription_id:
            cur.execute("INSERT INTO Subscription (Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval) VALUES (%s, %s, %s, %s, %s)", 
                       (customer_id, subscription_product_id, start_date, end_date or None, refill_interval))
            subscription_id = cur.lastrowid
            product_ids.append(subscription_product_id)
            quantities.append("1")

        # If a subscription is selected, fetch its product
        if subscription_id and not subscription_product_id:
            cur.execute("SELECT Product_ID FROM Subscription WHERE Subscription_ID = %s", (subscription_id,))
            subscription = cur.fetchone()
            if subscription:
                product_ids.append(str(subscription["Product_ID"]))
                quantities.append("1")

        # Always get and process normal products from Order Products section
        normal_product_ids = [pid for pid in request.form.getlist("product_id") if pid.strip()]
        normal_quantities = [qty for qty in request.form.getlist("quantity") if qty.strip()]
        
        # Ensure matching lengths and convert to integers
        min_length = min(len(normal_product_ids), len(normal_quantities))
        for i in range(min_length):
            try:
                product_id = int(normal_product_ids[i])
                quantity = int(normal_quantities[i])
                if product_id and quantity > 0:
                    product_ids.append(str(product_id))
                    quantities.append(str(quantity))
            except ValueError:
                continue  # Skip invalid entries

        # Process all products for the order
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty:
                continue
            product_id = int(pid)
            quantity = int(qty)

            cur.execute("SELECT Price, Quantity FROM Product WHERE Product_ID = %s", (product_id,))
            row = cur.fetchone()
            if not row:
                continue

            price = Decimal(str(row["Price"]))
            stock = row["Quantity"]
            if quantity > stock:
                continue

            cur.execute("""
                INSERT INTO Order_Product (Order_ID, Product_ID, Quantity, Unit_Price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
            cur.execute("""
                UPDATE Product SET Quantity = Quantity - %s WHERE Product_ID = %s
            """, (quantity, product_id))

            total_amount += (price * quantity)

        # Validate existing prescription or subscription
        if prescription_id:
            cur.execute("SELECT Prescription_ID FROM Prescription WHERE Prescription_ID = %s AND Customer_ID = %s", (prescription_id, customer_id))
            if not cur.fetchone():
                return redirect(url_for('new_sale'))

        if subscription_id:
            cur.execute("SELECT Subscription_ID FROM Subscription WHERE Subscription_ID = %s AND Customer_ID = %s", (subscription_id, customer_id))
            if not cur.fetchone():
                return redirect(url_for('new_sale'))

        # Apply insurance discount if any
        if insurance_discount > 0:
            discount_amt = total_amount * (insurance_discount / Decimal("100"))
            total_amount -= discount_amt

        total_amount = total_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Update the order with the final total and additional fields
        cur.execute("""
            UPDATE Orders 
            SET Total_Amount = %s, Prescription_ID = %s, Subscription_ID = %s 
            WHERE Order_ID = %s
        """, (total_amount, prescription_id, subscription_id, order_id))
        conn.commit()

        return redirect(url_for("sales"))

    except Exception as e:
        conn.rollback()
        return redirect(url_for('new_sale'))

    finally:
        cur.close()
        conn.close()

@app.route('/submit2', methods=['POST'])
def submit_sales2():
    if 'pharmacist_id' not in session:
        return redirect(url_for('login'))

    pharmacist_id = int(session['pharmacist_id'])
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('new_sale2'))

    cur = conn.cursor(dictionary=True)

    try:
        customer_id = int(request.form["customer_id"])
        payment_method = request.form.get("payment_method", None)
        insurance_discount = Decimal(request.form.get("insurance_discount", "0") or "0")
        order_date = date.today()
        total_amount = Decimal("0.00")

        # Insert initial order with placeholder total
        cur.execute("""
            INSERT INTO Orders (Customer_ID, Pharmacist_ID, Order_Date, Payment_Method, Total_Amount, Insurance_Discount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, pharmacist_id, order_date, payment_method, total_amount, insurance_discount))
        conn.commit()
        order_id = cur.lastrowid

        # Initialize product list
        product_ids = []
        quantities = []

        # Handle prescription if provided
        prescription_id = request.form.get("PrescriptionID") or None
        doctor_name = request.form.get("DoctorName")
        prescription_date = request.form.get("Date")
        notes = request.form.get("Notes")
        prescription_product_ids = request.form.getlist("PrescriptionProductID[]")
        dosages = request.form.getlist("Dosage[]")
        taken_times = request.form.getlist("TakenTimes[]")
        durations = request.form.getlist("Duration[]")
        prescription_quantities = request.form.getlist("PrescriptionQuantity[]")

        if doctor_name and prescription_date and not prescription_id:
            cur.execute("INSERT INTO Prescription (Customer_ID, Doctor_Name, Date, Notes) VALUES (%s, %s, %s, %s)", 
                       (customer_id, doctor_name, prescription_date, notes))
            prescription_id = cur.lastrowid
            for i in range(len(prescription_product_ids)):
                product_id = prescription_product_ids[i].strip()
                if product_id:
                    cur.execute("INSERT INTO Prescription_Product (Prescription_ID, Product_ID, Dosage, TakenTimes, Duration, Quantity) VALUES (%s, %s, %s, %s, %s, %s)", 
                               (prescription_id, product_id, dosages[i].strip() or None, taken_times[i].strip() or None, durations[i].strip() or None, prescription_quantities[i].strip() or None))
                    product_ids.append(product_id)
                    quantities.append(prescription_quantities[i].strip() or "1")

        # If a prescription is selected, fetch its products
        if prescription_id and not doctor_name:
            cur.execute("SELECT Product_ID, Quantity FROM Prescription_Product WHERE Prescription_ID = %s", (prescription_id,))
            prescription_products = cur.fetchall()
            for product in prescription_products:
                product_ids.append(str(product["Product_ID"]))
                quantities.append(str(product["Quantity"]))

        # Handle subscription if provided
        subscription_id = request.form.get("SubscriptionID") or None
        subscription_product_id = request.form.get("SubscriptionProductID")
        start_date = request.form.get("StartDate")
        end_date = request.form.get("EndDate")
        refill_interval = request.form.get("RefillInterval")

        if subscription_product_id and start_date and refill_interval and not subscription_id:
            cur.execute("INSERT INTO Subscription (Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval) VALUES (%s, %s, %s, %s, %s)", 
                       (customer_id, subscription_product_id, start_date, end_date or None, refill_interval))
            subscription_id = cur.lastrowid
            product_ids.append(subscription_product_id)
            quantities.append("1")

        # If a subscription is selected, fetch its product
        if subscription_id and not subscription_product_id:
            cur.execute("SELECT Product_ID FROM Subscription WHERE Subscription_ID = %s", (subscription_id,))
            subscription = cur.fetchone()
            if subscription:
                product_ids.append(str(subscription["Product_ID"]))
                quantities.append("1")

        # Always get and process normal products from Order Products section
        normal_product_ids = [pid for pid in request.form.getlist("product_id") if pid.strip()]
        normal_quantities = [qty for qty in request.form.getlist("quantity") if qty.strip()]
        
        # Ensure matching lengths and convert to integers
        min_length = min(len(normal_product_ids), len(normal_quantities))
        for i in range(min_length):
            try:
                product_id = int(normal_product_ids[i])
                quantity = int(normal_quantities[i])
                if product_id and quantity > 0:
                    product_ids.append(str(product_id))
                    quantities.append(str(quantity))
            except ValueError:
                continue  # Skip invalid entries

        # Process all products for the order
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty:
                continue
            product_id = int(pid)
            quantity = int(qty)

            cur.execute("SELECT Price, Quantity FROM Product WHERE Product_ID = %s", (product_id,))
            row = cur.fetchone()
            if not row:
                continue

            price = Decimal(str(row["Price"]))
            stock = row["Quantity"]
            if quantity > stock:
                continue

            cur.execute("""
                INSERT INTO Order_Product (Order_ID, Product_ID, Quantity, Unit_Price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
            cur.execute("""
                UPDATE Product SET Quantity = Quantity - %s WHERE Product_ID = %s
            """, (quantity, product_id))

            total_amount += (price * quantity)

        # Validate existing prescription or subscription
        if prescription_id:
            cur.execute("SELECT Prescription_ID FROM Prescription WHERE Prescription_ID = %s AND Customer_ID = %s", (prescription_id, customer_id))
            if not cur.fetchone():
                return redirect(url_for('new_sale2'))

        if subscription_id:
            cur.execute("SELECT Subscription_ID FROM Subscription WHERE Subscription_ID = %s AND Customer_ID = %s", (subscription_id, customer_id))
            if not cur.fetchone():
                return redirect(url_for('new_sale2'))

        # Apply insurance discount if any
        if insurance_discount > 0:
            discount_amt = total_amount * (insurance_discount / Decimal("100"))
            total_amount -= discount_amt

        total_amount = total_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Update the order with the final total and additional fields
        cur.execute("""
            UPDATE Orders 
            SET Total_Amount = %s, Prescription_ID = %s, Subscription_ID = %s 
            WHERE Order_ID = %s
        """, (total_amount, prescription_id, subscription_id, order_id))
        conn.commit()

        return redirect(url_for("sales2"))

    except Exception as e:
        conn.rollback()
        return redirect(url_for('new_sale2'))

    finally:
        cur.close()
        conn.close()

        
@app.route('/get_subscription_products/<int:subscription_id>')
def get_subscription_products(subscription_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT Product_ID FROM Subscription WHERE Subscription_ID = %s', (subscription_id,))
    subscription = cursor.fetchone()
    conn.close()
    return jsonify(subscription)

@app.route('/sale_archive', methods=['GET'])
def sale_archive():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            search_query = request.args.get('search', '', type=str).strip()

            if search_query.isdigit():
                query = '''
                    SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                           c.Name AS CustomerName
                    FROM Orders o
                    JOIN Order_Product op ON o.Order_ID = op.Order_ID
                    JOIN Product p ON op.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                    JOIN Customer c ON o.Customer_ID = c.Customer_ID
                    WHERE o.Order_ID = %s
                    ORDER BY o.Order_Date DESC
                '''
                cursor.execute(query, (search_query,))
            elif search_query:
                # Validate date format (YYYY-MM-DD)
                try:
                    from datetime import datetime
                    datetime.strptime(search_query, '%Y-%m-%d')
                    query = '''
                        SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                               o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                               c.Name AS CustomerName
                        FROM Orders o
                        JOIN Order_Product op ON o.Order_ID = op.Order_ID
                        JOIN Product p ON op.Product_ID = p.Product_ID
                        JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                        JOIN Customer c ON o.Customer_ID = c.Customer_ID
                        WHERE o.Order_Date = %s
                        ORDER BY o.Order_Date DESC
                    '''
                    cursor.execute(query, (search_query,))
                except ValueError:
                    return render_template('error.html', message="Invalid date format. Please use YYYY-MM-DD.")
            else:
                query = '''
                    SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                           c.Name AS CustomerName
                    FROM Orders o
                    JOIN Order_Product op ON o.Order_ID = op.Order_ID
                    JOIN Product p ON op.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                    JOIN Customer c ON o.Customer_ID = c.Customer_ID
                    ORDER BY o.Order_Date DESC
                '''
                cursor.execute(query)

            rows = cursor.fetchall()
            return render_template('sale_archive.html', rows=rows)

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

@app.route('/sale_archive2', methods=['GET'])
def sale_archive2():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            search_query = request.args.get('search', '', type=str).strip()

            if search_query.isdigit():
                query = '''
                    SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                           c.Name AS CustomerName
                    FROM Orders o
                    JOIN Order_Product op ON o.Order_ID = op.Order_ID
                    JOIN Product p ON op.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                    JOIN Customer c ON o.Customer_ID = c.Customer_ID
                    WHERE o.Order_ID = %s
                    ORDER BY o.Order_Date DESC
                '''
                cursor.execute(query, (search_query,))
            elif search_query:
                # Validate date format (YYYY-MM-DD)
                try:
                    from datetime import datetime
                    datetime.strptime(search_query, '%Y-%m-%d')
                    query = '''
                        SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                               o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                               c.Name AS CustomerName
                        FROM Orders o
                        JOIN Order_Product op ON o.Order_ID = op.Order_ID
                        JOIN Product p ON op.Product_ID = p.Product_ID
                        JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                        JOIN Customer c ON o.Customer_ID = c.Customer_ID
                        WHERE o.Order_Date = %s
                        ORDER BY o.Order_Date DESC
                    '''
                    cursor.execute(query, (search_query,))
                except ValueError:
                    return render_template('error.html', message="Invalid date format. Please use YYYY-MM-DD.")
            else:
                query = '''
                    SELECT o.Order_ID AS SalesID, ph.Name AS PharmsticName, p.Name AS ProductName,
                           o.Order_Date AS Date, op.Quantity, o.Payment_Method AS PaymentMethod,
                           c.Name AS CustomerName
                    FROM Orders o
                    JOIN Order_Product op ON o.Order_ID = op.Order_ID
                    JOIN Product p ON op.Product_ID = p.Product_ID
                    JOIN Pharmacist ph ON o.Pharmacist_ID = ph.Pharmacist_ID
                    JOIN Customer c ON o.Customer_ID = c.Customer_ID
                    ORDER BY o.Order_Date DESC
                '''
                cursor.execute(query)

            rows = cursor.fetchall()
            return render_template('sale_archive2.html', rows=rows)

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")


@app.route('/edit_sales/<int:id>', methods=['GET', 'POST'])
def edit_sales(id):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='PharmacyManagement'
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch sale details including all products
        cursor.execute('''
            SELECT o.Order_ID AS SalesID, o.Customer_ID AS CustomerID, o.Pharmacist_ID AS PharmacistID,
                   o.Order_Date AS OrderDate, o.Payment_Method AS PaymentMethod,
                   op.Product_ID AS ProductID, op.Quantity, op.Unit_Price, p.Name AS ProductName
            FROM Orders o
            JOIN Order_Product op ON o.Order_ID = op.Order_ID
            JOIN Product p ON op.Product_ID = p.Product_ID
            WHERE o.Order_ID = %s
        ''', (id,))
        sales = cursor.fetchall()

        if not sales:
            conn.close()
            return render_template('error.html', message=f"Sale with ID {id} not found.")

        if request.method == 'POST':
            if 'pharmacist_id' not in session:
                conn.close()
                return redirect(url_for('login'))

            customer_id = request.form.get('CustomerID')
            pharmacist_id = request.form.get('PharmacistID')
            payment_method = request.form.get('PaymentMethod')
            product_ids = request.form.getlist('ProductID[]')
            quantities = request.form.getlist('Quantity[]')
            order_date = request.form.get('OrderDate')

            if not customer_id or not customer_id.strip().isdigit():
                conn.close()
                return render_template('error.html', message="Customer ID must be a valid number.")
            customer_id = int(customer_id)

            if not pharmacist_id or not pharmacist_id.strip().isdigit():
                conn.close()
                return render_template('error.html', message="Pharmacist ID must be a valid number.")
            pharmacist_id = int(pharmacist_id)

            if not product_ids or not all(pid.strip().isdigit() for pid in product_ids):
                conn.close()
                return render_template('error.html', message="Product ID must be a valid number.")
            product_ids = [int(pid) for pid in product_ids]

            if not quantities or not all(qty.strip().isdigit() for qty in quantities):
                conn.close()
                return render_template('error.html', message="Quantity must be a valid number.")
            quantities = [int(qty) for qty in quantities]

            if len(product_ids) != len(quantities):
                conn.close()
                return render_template('error.html', message="Number of Product IDs and Quantities must match.")

            cursor.execute('SELECT Customer_ID FROM Customer WHERE Customer_ID = %s', (customer_id,))
            if not cursor.fetchone():
                conn.close()
                return render_template('error.html', message=f"Customer ID {customer_id} does not exist.")

            cursor.execute('SELECT Pharmacist_ID FROM Pharmacist WHERE Pharmacist_ID = %s', (pharmacist_id,))
            if not cursor.fetchone():
                conn.close()
                return render_template('error.html', message=f"Pharmacist ID {pharmacist_id} does not exist.")

            # Restore old stock
            cursor.execute('SELECT Product_ID, Quantity FROM Order_Product WHERE Order_ID = %s', (id,))
            old_products = cursor.fetchall()
            for old_product in old_products:
                cursor.execute('UPDATE Product SET Quantity = Quantity + %s WHERE Product_ID = %s', 
                              (old_product['Quantity'], old_product['Product_ID']))

            # Delete existing Order_Product entries
            cursor.execute('DELETE FROM Order_Product WHERE Order_ID = %s', (id,))

            # Process all new products
            total_amount = 0
            for pid, qty in zip(product_ids, quantities):
                product_id = int(pid)
                quantity = int(qty)

                cursor.execute('SELECT Name, Quantity, Price FROM Product WHERE Product_ID = %s', (product_id,))
                product = cursor.fetchone()
                if not product:
                    conn.close()
                    return render_template('error.html', message=f"Product ID {product_id} not found.")
                product_name = product['Name']
                current_stock = product['Quantity'] if product['Quantity'] is not None else 0
                price = product['Price']

                if current_stock == 0:
                    cursor.execute('''
                        SELECT Product_ID, Name 
                        FROM Product 
                        WHERE Description = (SELECT Description FROM Product WHERE Product_ID = %s) 
                        AND Quantity > 0 AND Product_ID != %s LIMIT 1
                    ''', (product_id, product_id))
                    alternative = cursor.fetchone()
                    conn.close()
                    if alternative:
                        alternative_id = alternative['Product_ID']
                        alternative_name = alternative['Name']
                        return render_template(
                            'error.html', 
                            message=f"Product {product_name} (ID: {product_id}) is out of stock. Consider Product ID {alternative_id} ({alternative_name}) instead.")
                    return render_template(
                        'error.html', 
                        message=f"Product {product_name} (ID: {product_id}) is out of stock, and no alternatives are available.")

                if quantity > current_stock:
                    conn.close()
                    return render_template(
                        'error.html', 
                        message=f"Requested quantity ({quantity}) for Product {product_name} (ID: {product_id}) exceeds available stock ({current_stock}).")

                # Insert new Order_Product entry and update stock
                cursor.execute('''
                    INSERT INTO Order_Product (Order_ID, Product_ID, Quantity, Unit_Price)
                    VALUES (%s, %s, %s, %s)
                ''', (id, product_id, quantity, price))
                cursor.execute('UPDATE Product SET Quantity = Quantity - %s WHERE Product_ID = %s', (quantity, product_id))
                total_amount += quantity * price

            # Update Orders table
            cursor.execute('''
                UPDATE Orders 
                SET Customer_ID = %s, Pharmacist_ID = %s, Order_Date = %s, Payment_Method = %s,
                    Total_Amount = %s
                WHERE Order_ID = %s
            ''', (customer_id, pharmacist_id, order_date, payment_method, total_amount, id))

            conn.commit()
            conn.close()
            return redirect(url_for('sale_archive'))

        conn.close()
        return render_template('edit_sale.html', sales=sales)

    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return render_template('out_of_stock.html', message=f"An error occurred: {str(e)}")

@app.route('/edit_sales2/<int:id>', methods=['GET', 'POST'])
def edit_sales2(id):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='PharmacyManagement'
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch sale details including all products
        cursor.execute('''
            SELECT o.Order_ID AS SalesID, o.Customer_ID AS CustomerID, o.Pharmacist_ID AS PharmacistID,
                   o.Order_Date AS OrderDate, o.Payment_Method AS PaymentMethod,
                   op.Product_ID AS ProductID, op.Quantity, op.Unit_Price, p.Name AS ProductName
            FROM Orders o
            JOIN Order_Product op ON o.Order_ID = op.Order_ID
            JOIN Product p ON op.Product_ID = p.Product_ID
            WHERE o.Order_ID = %s
        ''', (id,))
        sales = cursor.fetchall()  # Get all products for the order

        if not sales:
            conn.close()
            return render_template('error.html', message=f"Sale with ID {id} not found.")

        if request.method == 'POST':
            if 'pharmacist_id' not in session:
                conn.close()
                return redirect(url_for('login'))

            customer_id = request.form.get('CustomerID')
            pharmacist_id = request.form.get('PharmacistID')
            payment_method = request.form.get('PaymentMethod')
            product_ids = request.form.getlist('ProductID[]')
            quantities = request.form.getlist('Quantity[]')
            order_date = request.form.get('OrderDate')

            if not customer_id or not customer_id.strip().isdigit():
                conn.close()
                return render_template('error.html', message="Customer ID must be a valid number.")
            customer_id = int(customer_id)

            if not pharmacist_id or not pharmacist_id.strip().isdigit():
                conn.close()
                return render_template('error.html', message="Pharmacist ID must be a valid number.")
            pharmacist_id = int(pharmacist_id)

            if not product_ids or not all(pid.strip().isdigit() for pid in product_ids):
                conn.close()
                return render_template('error.html', message="Product ID must be a valid number.")
            product_ids = [int(pid) for pid in product_ids]

            if not quantities or not all(qty.strip().isdigit() for qty in quantities):
                conn.close()
                return render_template('error.html', message="Quantity must be a valid number.")
            quantities = [int(qty) for qty in quantities]

            if len(product_ids) != len(quantities):
                conn.close()
                return render_template('error.html', message="Number of Product IDs and Quantities must match.")

            cursor.execute('SELECT Customer_ID FROM Customer WHERE Customer_ID = %s', (customer_id,))
            if not cursor.fetchone():
                conn.close()
                return render_template('error.html', message=f"Customer ID {customer_id} does not exist.")

            cursor.execute('SELECT Pharmacist_ID FROM Pharmacist WHERE Pharmacist_ID = %s', (pharmacist_id,))
            if not cursor.fetchone():
                conn.close()
                return render_template('error.html', message=f"Pharmacist ID {pharmacist_id} does not exist.")

            # Restore old stock
            cursor.execute('SELECT Product_ID, Quantity FROM Order_Product WHERE Order_ID = %s', (id,))
            old_products = cursor.fetchall()
            for old_product in old_products:
                cursor.execute('UPDATE Product SET Quantity = Quantity + %s WHERE Product_ID = %s', 
                              (old_product['Quantity'], old_product['Product_ID']))

            # Delete existing Order_Product entries
            cursor.execute('DELETE FROM Order_Product WHERE Order_ID = %s', (id,))

            # Process all new products
            total_amount = 0
            for pid, qty in zip(product_ids, quantities):
                product_id = int(pid)
                quantity = int(qty)

                cursor.execute('SELECT Name, Quantity, Price FROM Product WHERE Product_ID = %s', (product_id,))
                product = cursor.fetchone()
                if not product:
                    conn.close()
                    return render_template('error.html', message=f"Product ID {product_id} not found.")
                product_name = product['Name']
                current_stock = product['Quantity'] if product['Quantity'] is not None else 0
                price = product['Price']

                if current_stock == 0:
                    cursor.execute('''
                        SELECT Product_ID, Name 
                        FROM Product 
                        WHERE Description = (SELECT Description FROM Product WHERE Product_ID = %s) 
                        AND Quantity > 0 AND Product_ID != %s LIMIT 1
                    ''', (product_id, product_id))
                    alternative = cursor.fetchone()
                    conn.close()
                    if alternative:
                        alternative_id = alternative['Product_ID']
                        alternative_name = alternative['Name']
                        return render_template(
                            'error.html', 
                            message=f"Product {product_name} (ID: {product_id}) is out of stock. Consider Product ID {alternative_id} ({alternative_name}) instead.")
                    return render_template(
                        'error.html', 
                        message=f"Product {product_name} (ID: {product_id}) is out of stock, and no alternatives are available.")

                if quantity > current_stock:
                    conn.close()
                    return render_template(
                        'error.html', 
                        message=f"Requested quantity ({quantity}) for Product {product_name} (ID: {product_id}) exceeds available stock ({current_stock}).")

                # Insert new Order_Product entry and update stock
                cursor.execute('''
                    INSERT INTO Order_Product (Order_ID, Product_ID, Quantity, Unit_Price)
                    VALUES (%s, %s, %s, %s)
                ''', (id, product_id, quantity, price))
                cursor.execute('UPDATE Product SET Quantity = Quantity - %s WHERE Product_ID = %s', (quantity, product_id))
                total_amount += quantity * price

            # Update Orders table
            cursor.execute('''
                UPDATE Orders 
                SET Customer_ID = %s, Pharmacist_ID = %s, Order_Date = %s, Payment_Method = %s,
                    Total_Amount = %s
                WHERE Order_ID = %s
            ''', (customer_id, pharmacist_id, order_date, payment_method, total_amount, id))

            conn.commit()
            conn.close()
            return redirect(url_for('sale_archive2'))

        conn.close()
        return render_template('edit_sale2.html', sales=sales)

    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return render_template('out_of_stock2.html', message=f"An error occurred: {str(e)}")
    
    
@app.route('/delete_sales/<int:id>', methods=['GET', 'POST'])
def delete_sales(id):
    try:
        # Check if pharmacist is logged in
        if 'pharmacist_id' not in session:
            return redirect(url_for('login'))

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Check if order exists and fetch associated products
            cursor.execute('''
                SELECT op.Product_ID, op.Quantity
                FROM Order_Product op
                WHERE op.Order_ID = %s
            ''', (id,))
            order_products = cursor.fetchall()

            cursor.execute('SELECT Order_ID FROM Orders WHERE Order_ID = %s', (id,))
            order = cursor.fetchone()

            if not order:
                return render_template('error.html', message=f"Sale with ID {id} not found.")

            # Restore product quantities
            for product in order_products:
                cursor.execute('''
                    UPDATE Product 
                    SET Quantity = Quantity + %s 
                    WHERE Product_ID = %s
                ''', (product['Quantity'], product['Product_ID']))

            # Delete from Order_Product and Orders (in that order due to foreign key constraints)
            cursor.execute('DELETE FROM Order_Product WHERE Order_ID = %s', (id,))
            cursor.execute('DELETE FROM Orders WHERE Order_ID = %s', (id,))

            conn.commit()

        return redirect(url_for('sale_archive'))

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

@app.route('/delete_sales2/<int:id>', methods=['GET', 'POST'])
def delete_sales2(id):
    try:
        # Check if pharmacist is logged in
        if 'pharmacist_id' not in session:
            return redirect(url_for('login'))

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute('''
                SELECT op.Product_ID, op.Quantity
                FROM Order_Product op
                WHERE op.Order_ID = %s
            ''', (id,))
            order_products = cursor.fetchall()

            cursor.execute('SELECT Order_ID FROM Orders WHERE Order_ID = %s', (id,))
            order = cursor.fetchone()

            if not order:
                return render_template('error.html', message=f"Sale with ID {id} not found.")

            for product in order_products:
                cursor.execute('''
                    UPDATE Product 
                    SET Quantity = Quantity + %s 
                    WHERE Product_ID = %s
                ''', (product['Quantity'], product['Product_ID']))

            cursor.execute('DELETE FROM Order_Product WHERE Order_ID = %s', (id,))
            cursor.execute('DELETE FROM Orders WHERE Order_ID = %s', (id,))

            conn.commit()

        return redirect(url_for('sale_archive2'))

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

@app.route('/manage_prescriptions')
def manage_prescriptions():
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to the database!")
            return render_template('error.html', message="Database connection failed.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT Prescription_ID, Customer_ID, Doctor_Name, Date, Notes FROM Prescription')
        prescriptions = cursor.fetchall()
        print(f"Fetched prescriptions: {prescriptions}") 

        if not prescriptions:
            print("No prescriptions found in the database.")

        conn.close()
        return render_template('manage_prescriptions.html', prescriptions=prescriptions)

    except Error as e:
        print(f"Error fetching prescriptions: {e}")
        if 'conn' in locals():
            conn.close()
        return render_template('error.html', message=f"Error fetching prescriptions: {str(e)}")

@app.route('/manage_prescriptions2')
def manage_prescriptions2():
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to the database!")
            return render_template('error.html', message="Database connection failed.")

        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT Prescription_ID, Customer_ID, Doctor_Name, Date, Notes FROM Prescription')
        prescriptions = cursor.fetchall()
        print(f"Fetched prescriptions: {prescriptions}")  

        if not prescriptions:
            print("No prescriptions found in the database.")

        conn.close()
        return render_template('manage_prescriptions2.html', prescriptions=prescriptions)

    except Error as e:
        print(f"Error fetching prescriptions: {e}")
        if 'conn' in locals():
            conn.close()
        return render_template('error.html', message=f"Error fetching prescriptions: {str(e)}")


@app.route('/edit_prescription/<int:prescription_id>', methods=['GET', 'POST'])
def edit_prescription(prescription_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        doctor_name = request.form['doctor_name']
        date = request.form['date']
        notes = request.form['notes']
        
        query = """
            UPDATE Prescription
            SET Customer_ID = %s, Doctor_Name = %s, Date = %s, Notes = %s
            WHERE Prescription_ID = %s
        """
        cursor.execute(query, (customer_id, doctor_name, date, notes, prescription_id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_prescriptions'))
    
    cursor.execute('SELECT * FROM Prescription WHERE Prescription_ID = %s', (prescription_id,))
    prescription = cursor.fetchone()
    conn.close()
    
    if not prescription:
        return redirect(url_for('manage_prescriptions'))
    
    return render_template('edit_prescription.html', prescription=prescription)


@app.route('/edit_prescription2/<int:prescription_id>', methods=['GET', 'POST'])
def edit_prescription2(prescription_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        doctor_name = request.form['doctor_name']
        date = request.form['date']
        notes = request.form['notes']
        
        query = """
            UPDATE Prescription
            SET Customer_ID = %s, Doctor_Name = %s, Date = %s, Notes = %s
            WHERE Prescription_ID = %s
        """
        cursor.execute(query, (customer_id, doctor_name, date, notes, prescription_id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_prescriptions2'))
    
    cursor.execute('SELECT * FROM Prescription WHERE Prescription_ID = %s', (prescription_id,))
    prescription = cursor.fetchone()
    conn.close()
    
    if not prescription:
        return redirect(url_for('manage_prescriptions2'))
    
    return render_template('edit_prescription2.html', prescription=prescription)

@app.route('/delete_prescription/<int:prescription_id>', methods=['POST'])
def delete_prescription(prescription_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Prescription WHERE Prescription_ID = %s', (prescription_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_prescriptions'))

@app.route('/delete_prescription2/<int:prescription_id>', methods=['POST'])
def delete_prescription2(prescription_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Prescription WHERE Prescription_ID = %s', (prescription_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_prescriptions2'))


@app.route('/subscriptions', methods=['GET'])
def subscriptions():
    conn = None
    cursor1 = None
    cursor2 = None
    rows = []
    topSubscription = None

    try:
        conn = get_db_connection()
        if conn is None:
            raise Error("Failed to get database connection")
        conn = ensure_connection(conn)

        cursor1 = conn.cursor(dictionary=True, buffered=True)
        search_query = request.args.get('search', default='', type=str)

        if search_query.isdigit():
            cursor1.execute("SELECT * FROM Subscription WHERE Subscription_ID = %s", (search_query,))
        elif search_query:
            cursor1.execute("SELECT * FROM Subscription s JOIN Product p ON s.Product_ID = p.Product_ID WHERE p.Name LIKE %s", (f"%{search_query}%",))
        else:
            cursor1.execute("SELECT Subscription_ID, Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval FROM Subscription")

        rows = cursor1.fetchall()

        cursor2 = conn.cursor(dictionary=True, buffered=True)
        first_day_of_month = datetime(2025, 6, 1).strftime("%Y-%m-%d")
        query = """
            SELECT s.Subscription_ID, c.Name, p.Name, s.Start_Date, s.End_Date
            FROM Subscription s
            JOIN Customer c ON s.Customer_ID = c.Customer_ID
            JOIN Product p ON s.Product_ID = p.Product_ID
            LEFT JOIN Order_Product op ON p.Product_ID = op.Product_ID
            LEFT JOIN Orders o ON op.Order_ID = o.Order_ID
            WHERE s.Start_Date >= %s
        """
        cursor2.execute(query, (first_day_of_month,))
        topSubscription = cursor2.fetchone()

    except Error as e:
        print(f"Error in subscriptions: {e}")
        return "Database error occurred. Please try again later."
    finally:
        if cursor1:
            cursor1.close()
        if cursor2:
            cursor2.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template('subscriptions.html', rows=rows, topSubscription=topSubscription)

@app.route('/subscriptions2', methods=['GET'])
def subscriptions2():
    conn = None
    cursor1 = None
    cursor2 = None
    rows = []
    topSubscription = None

    try:
        conn = get_db_connection()
        if conn is None:
            raise Error("Failed to get database connection")
        conn = ensure_connection(conn)


        cursor1 = conn.cursor(dictionary=True, buffered=True)
        search_query = request.args.get('search', default='', type=str)

        if search_query.isdigit():
            cursor1.execute("SELECT * FROM Subscription WHERE Subscription_ID = %s", (search_query,))
        elif search_query:
            cursor1.execute("SELECT * FROM Subscription s JOIN Product p ON s.Product_ID = p.Product_ID WHERE p.Name LIKE %s", (f"%{search_query}%",))
        else:
            cursor1.execute("SELECT Subscription_ID, Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval FROM Subscription")

        rows = cursor1.fetchall()


        cursor2 = conn.cursor(dictionary=True, buffered=True)
        first_day_of_month = datetime(2025, 6, 1).strftime("%Y-%m-%d")
        query = """
            SELECT s.Subscription_ID, c.Name, p.Name, s.Start_Date, s.End_Date
            FROM Subscription s
            JOIN Customer c ON s.Customer_ID = c.Customer_ID
            JOIN Product p ON s.Product_ID = p.Product_ID
            LEFT JOIN Order_Product op ON p.Product_ID = op.Product_ID
            LEFT JOIN Orders o ON op.Order_ID = o.Order_ID
            WHERE s.Start_Date >= %s
        """
        cursor2.execute(query, (first_day_of_month,))
        topSubscription = cursor2.fetchone()

    except Error as e:
        print(f"Error in subscriptions2: {e}")
        return "Database error occurred. Please try again later."
    finally:
        if cursor1:
            cursor1.close()
        if cursor2:
            cursor2.close()
        if conn and conn.is_connected():
            conn.close()

    return render_template('subscriptions2.html', rows=rows, topSubscription=topSubscription)

@app.route('/add_subscription', methods=['GET', 'POST'])
def add_subscription():
    if request.method == 'POST':
        customer_id = request.form['CustomerID']
        product_id = request.form['ProductID']
        start_date = request.form['StartDate']
        end_date = request.form['EndDate']
        refill_interval = request.form['RefillInterval']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Subscription (Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval) VALUES (%s, %s, %s, %s, %s)',
                           (customer_id, product_id, start_date, end_date, refill_interval))
            conn.commit()
        return redirect(url_for('subscriptions'))
    return render_template('add_subscription.html')

@app.route('/add_subscription2', methods=['GET', 'POST'])
def add_subscription2():
    if request.method == 'POST':
        customer_id = request.form['CustomerID']
        product_id = request.form['ProductID']
        start_date = request.form['StartDate']
        end_date = request.form['EndDate']
        refill_interval = request.form['RefillInterval']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO Subscription (Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval) VALUES (%s, %s, %s, %s, %s)',
                           (customer_id, product_id, start_date, end_date, refill_interval))
            conn.commit()
        return redirect(url_for('subscriptions2'))
    return render_template('add_subscription2.html')

@app.route('/edit_subscription/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Subscription WHERE Subscription_ID = %s', (subscription_id,))
        subscription = cursor.fetchone()

        if not subscription:
            return redirect(url_for('manage_subscription.html'))

        if request.method == 'POST':
            customer_id = request.form['customer_id']
            product_id = request.form['product_id']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            refill_interval = request.form['refill_interval']
            cursor.execute('''
                UPDATE Subscription 
                SET Customer_ID = %s, Product_ID = %s, Start_Date = %s, End_Date = %s, Refill_Interval = %s
                WHERE Subscription_ID = %s
            ''', (customer_id, product_id, start_date, end_date, refill_interval, subscription_id))
            conn.commit()
            return redirect(url_for('subscriptions'))

    return render_template('edit_subscription.html', subscription=subscription)

@app.route('/edit_subscription2/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription2(subscription_id):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Subscription WHERE Subscription_ID = %s', (subscription_id,))
        subscription = cursor.fetchone()

        if not subscription:
            return redirect(url_for('subscriptions2'))

        if request.method == 'POST':
            customer_id = request.form['customer_id']
            product_id = request.form['product_id']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            refill_interval = request.form['refill_interval']
            cursor.execute('''
                UPDATE Subscription 
                SET Customer_ID = %s, Product_ID = %s, Start_Date = %s, End_Date = %s, Refill_Interval = %s
                WHERE Subscription_ID = %s
            ''', (customer_id, product_id, start_date, end_date, refill_interval, subscription_id))
            conn.commit()
            return redirect(url_for('subscriptions2'))

    return render_template('edit_subscription2.html', subscription=subscription)

@app.route('/delete_subscription/<int:subscription_id>', methods=['GET', 'POST'])
def delete_subscription(subscription_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Subscription WHERE Subscription_ID = %s', (subscription_id,))
        conn.commit()
    return redirect(url_for('subscriptions'))

@app.route('/delete_subscription2/<int:subscription_id>', methods=['GET', 'POST'])
def delete_subscription2(subscription_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Subscription WHERE Subscription_ID = %s', (subscription_id,))
        conn.commit()
    return redirect(url_for('subscriptions2'))



########################################################################
##Queries
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='PharmacyManagement'
    )

#main page for the reports
@app.route('/reports')
def reports():
    return render_template('report_selection.html')

#top 5 Most Sold product('Capsule', 'Syrup', 'Tablet') and will display the quantity that was sold
@app.route('/report1')
def report1():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.Name AS ProductName, 
            SUM(op.Quantity) AS TotalSold
        FROM 
            Product p
        LEFT JOIN 
            Order_Product op ON p.Product_ID = op.Product_ID
        LEFT JOIN 
            Orders o ON op.Order_ID = o.Order_ID
        WHERE 
            p.Type IN ('Capsule', 'Syrup', 'Tablet') 
        GROUP BY 
            p.Name
        ORDER BY 
            TotalSold DESC
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report1.html', rows=rows)

#total sales revenue per pharmacist
@app.route('/report2')
def report2():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            ph.Name AS PharmacistName, 
            SUM(o.Total_Amount) AS TotalRevenue
        FROM 
            Pharmacist ph
        LEFT JOIN 
            Orders o ON ph.Pharmacist_ID = o.Pharmacist_ID
        GROUP BY 
            ph.Name
        ORDER BY 
            TotalRevenue DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report2.html', rows=rows)

#top 5 customers by total amount spent
@app.route('/report3')
def report3():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            c.Name AS CustomerName, 
            SUM(o.Total_Amount) AS TotalSpent
        FROM 
            Customer c
        LEFT JOIN 
            Orders o ON c.Customer_ID = o.Customer_ID
        GROUP BY 
            c.Name
        ORDER BY 
            TotalSpent DESC
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report3.html', rows=rows)

#products that are close to expiring and have quantity > 50
@app.route('/report4')
def report4():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    current_date = datetime.now().strftime("%Y-%m-%d")
    query = """
        SELECT 
            Name AS ProductName, 
            Expiration_Date AS ExpirationDate, 
            Quantity
        FROM 
            Product
        WHERE 
            Expiration_Date <= DATE_ADD(%s, INTERVAL 30 DAY)
            AND Quantity > 50;
    """
    cursor.execute(query, (current_date,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report4.html', rows=rows)

#total quantity sold for each product type 
@app.route('/report5')
def report5():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.Type AS ProductType, 
            SUM(op.Quantity) AS TotalQuantitySold
        FROM 
            Product p
        LEFT JOIN 
            Order_Product op ON p.Product_ID = op.Product_ID
        GROUP BY 
            p.Type;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report5.html', rows=rows)

#average and maximum wages of pharmacists grouped by their roles
@app.route('/report6')
def report6():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            Role, 
            AVG(Wage) AS AvgWage, 
            MAX(Wage) AS MaxWage
        FROM 
            Pharmacist
        GROUP BY 
            Role;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report6.html', rows=rows)

#most frequently purchased product (highest total quantity purchased)
@app.route('/report7')
def report7():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.Name AS ProductName, 
            SUM(po.Quantity) AS TotalPurchased
        FROM 
            Product p
        LEFT JOIN 
            Purchase_Order po ON p.Product_ID = po.Product_ID
        GROUP BY 
            p.Name
        ORDER BY 
            TotalPurchased DESC
        LIMIT 1;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report7.html', rows=rows)

#total quantity ordered by each pharmacist
@app.route('/report8')
def report8():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            ph.Name AS PharmacistName, 
            SUM(po.Quantity) AS TotalQuantityOrdered
        FROM 
            Pharmacist ph
        LEFT JOIN 
            Purchase_Order po ON ph.Pharmacist_ID = po.Pharmacist_ID
        GROUP BY 
            ph.Name;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report8.html', rows=rows)

#top 5 customers by active prescriptions and subscriptions
@app.route('/report9')
def report9():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            c.Name AS CustomerName,
            COUNT(DISTINCT s.Subscription_ID) AS ActiveSubscriptions,
            COUNT(DISTINCT p.Prescription_ID) AS ActivePrescriptions,
            (COUNT(DISTINCT s.Subscription_ID) + COUNT(DISTINCT p.Prescription_ID)) AS TotalActivity
        FROM 
            Customer c
        LEFT JOIN 
            Subscription s ON c.Customer_ID = s.Customer_ID AND s.End_Date >= CURDATE()
        LEFT JOIN 
            Prescription p ON c.Customer_ID = p.Customer_ID AND p.Date <= CURDATE() AND (p.Date + INTERVAL 30 DAY) >= CURDATE()
        GROUP BY 
            c.Name
        ORDER BY 
            TotalActivity DESC
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report9.html', rows=rows)

#products with low stock (less than 30) and their reorder frequency
@app.route('/report10')
def report10():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.Name AS ProductName, 
            p.Quantity AS CurrentStock, 
            SUM(po.Quantity) AS ReorderFrequency
        FROM 
            Product p
        LEFT JOIN 
            Purchase_Order po ON p.Product_ID = po.Product_ID
        WHERE 
            p.Quantity < 30
        GROUP BY 
            p.Name, p.Quantity;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report10.html', rows=rows)

#highest earning payment method
@app.route('/report11')
def report11():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            o.Payment_Method AS PaymentMethod, 
            SUM(o.Total_Amount) AS TotalRevenue
        FROM 
            Orders o
        GROUP BY 
            o.Payment_Method
        ORDER BY 
            TotalRevenue DESC
        LIMIT 1;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report11.html', rows=rows)

#products with no sales recorded yet
@app.route('/report12')
def report12():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT 
            p.Name AS ProductName
        FROM 
            Product p
        LEFT JOIN 
            Order_Product op ON p.Product_ID = op.Product_ID
        WHERE 
            op.Product_ID IS NULL;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('report12.html', rows=rows)


@app.route('/', methods=['GET'])
def home():
    if 'logout' in request.args:  
        session.pop('user', None)  
    return render_template('login.html')


@app.route('/dashboard2')
def dashboard2():
    return render_template('dashboard2.html')



if __name__ == '__main__':
    app.run(debug=True)