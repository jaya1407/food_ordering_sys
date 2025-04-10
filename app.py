from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = 'jaya123'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jaya2003'  # Change as per your MySQL password
app.config['MYSQL_DB'] = 'food_order_db'

mysql = MySQL(app)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

# Menu Route
@app.route('/menu')
def menu():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM menu")
    menu_items = cur.fetchall()
    cur.close()
    return render_template('menu.html', menu_items=menu_items)

# Order Route
@app.route('/order', methods=['POST'])
def order():
    if 'username' not in session:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))

    food_id = request.form['food_id']
    quantity = int(request.form['quantity'])

    cur = mysql.connection.cursor()
    cur.execute("SELECT name, price FROM menu WHERE id = %s", (food_id,))
    food_item = cur.fetchone()
    total_price = food_item[1] * quantity

    cur.execute("INSERT INTO orders (username, food_item, quantity, total_price) VALUES (%s, %s, %s, %s)",
                (session['username'], food_item[0], quantity, total_price))
    mysql.connection.commit()
    cur.close()

    flash('Order placed successfully!', 'success')
    return redirect(url_for('view_orders'))

# View Orders Route
@app.route('/orders')
def view_orders():
    if 'username' not in session:
        flash('Please log in to view orders.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE username = %s", (session['username'],))
    orders = cur.fetchall()
    cur.close()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)