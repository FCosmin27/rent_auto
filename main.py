from database_management import *
from flask import Flask,render_template,redirect


app=Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/create-tables',methods=['POST'])
def handle_create_tables():
    try:
        create_tables_and_constraints()
    except Exception as e:
        return render_template('home.html',text='Tables already exist')
    return render_template('home.html',text=F'Tables created')


@app.route('/delete-tables',methods=['POST'])
def handle_delete_tables():
    delete_tables()
    return render_template('home.html',text='Tables deleted')

@app.route('/insert-data',methods=['POST'])
def handle_insert_data():
    try:
        insert_values()
    except Exception as e:
        return render_template('home.html',text='Data already inserted or tables do not exist')
    return render_template('home.html',text='Data inserted')

@app.route('/customers')
def handle_get_customers():
    conn=connect_to_database()
    cursor=conn.cursor()

    try:
        cursor.execute('SELECT * FROM cont_client')
        customers=cursor.fetchall()
        cursor.execute('SELECT * FROM date_individ')
        customers_info=cursor.fetchall()
    except Exception as e:
        return render_template('customers.html')
    return render_template('customers.html',customers=customers,customer_info=customers_info)


@app.route('/add-account',methods=['POST'])
def handle_add_account():
    conn=connect_to_database()
    cursor=conn.cursor()

    phone_acc=request.form['phone_acc']

    try:
        cursor.execute('SELECT * FROM cont_client')
        customers=cursor.fetchall()
    except Exception as e:
        return render_template('add_account.html')
    return render_template('add_account.html',customers=customers)



