from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

app = Flask(__name__)
app.secret_key = REDACTED

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    else:
        return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        query = 'SELECT * FROM users WHERE username=%s AND password=%s'
        values = (username, password)

        cursor.execute(query, values)
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]

            flash('Login is Successful', 'success')
            return redirect(url_for('dashboard'))
        
        else:
            flash('Invalid Credentials', 'danger')
            

        cursor.close()
        connection.close()

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']


        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        if cursor.fetchone():
            flash(username + " already exists", 'danger')
        else:
            query = 'INSERT INTO users(username, password, email) VALUES(%s, %s, %s);'
            values = (username, password, email)
            cursor.execute(query, values)
            connection.commit()

            flash(username + ' has been registered successfully!!!', 'success')
            return redirect(url_for('login'))


        cursor.close()
        connection.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
   session.clear()
   flash('You have been logged out', 'info')
   return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please Login in first', 'warning')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    query = 'SELECT SUM(amount) FROM expenses WHERE user_id = %s'
    values = (session['user_id'],)

    cursor.execute(query, values)
    row = cursor.fetchone()
    total = row[0]

    cursor.close()
    connection.close()

    return render_template('dashboard.html', total=total, username=session['username'])

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        flash('Please Login first', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']


        connection = get_db_connection()
        cursor = connection.cursor()


        user_id = session['user_id']


        query = 'INSERT INTO expenses(user_id, date, category, amount, description) VALUES(%s, %s, %s, %s, %s);'
        values = (user_id, date, category, amount, description)
        cursor.execute(query, values)
        connection.commit()


        flash('Expense added successfully!', 'success')
        
        cursor.close()
        connection.close()
        
        return redirect(url_for('view_expenses'))
    
    return render_template('add_expense.html')

@app.route('/view_expenses')
def view_expenses():
    if 'user_id' not in session:
        flash('Please Login first', 'warning')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary = True)

    user_id = session['user_id']

    query = 'SELECT * FROM expenses WHERE user_id = %s'
    values = (user_id,)

    cursor.execute(query, values)
    expenses = cursor.fetchall()
    print(expenses)

    cursor.close()
    connection.close()
    
    return render_template('view_expenses.html', expenses=expenses)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
   if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = 'UPDATE expenses SET date=%s, category=%s, amount=%s, description=%s WHERE id=%s AND user_id=%s'
        values = (date, category, amount, description, id, session['user_id']) 

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        message = f"Expense with id {id} is updated successfully!" 
        flash(message, 'success')
        return redirect(url_for('view_expenses'))
   else:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM expenses WHERE id=%s AND user_id=%s"
        values = (id, session['user_id'])
        cursor.execute(query, values)

        expenses = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template('edit.html', expenses=expenses)
    
       
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = 'DELETE FROM expenses WHERE id=%s'
    values = (id,)
    cursor.execute(query, values)
    connection.commit()
    
    message = f"Expense with id {id} is deleted successfully!" 
    flash(message, 'success')
    return redirect(url_for('view_expenses'))

if __name__ == '__main__':
    app.run(debug=True)

