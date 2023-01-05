from database_management import *
from flask import Flask,render_template,redirect,request


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
    phone_acc = request.form['phone_acc']
    email=request.form['email']

    try:
        cursor.execute("INSERT INTO cont_client (nr_telefon,email) VALUES (%s,%s)",(phone_acc,email))
    except Exception as e:
        return render_template('home.html',text=f'Invalid Insert, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')

@app.route('/add-personal-info',methods=['POST'])
def handle_add_personal_info():
    conn=connect_to_database()
    cursor=conn.cursor()
    phone_pers_info=request.form['phone_pers_info']
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    birth_date=request.form['birth_date']

    try:
        cursor.execute("INSERT INTO date_individ (nr_telefon,nume,prenume,data_nasterii) VALUES (%s,%s,%s,%s)",(phone_pers_info,last_name,first_name,birth_date))
    except Exception as e:
        return render_template('home.html',text=f'Invalid Insert, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')


@app.route('/remove-account',methods=['POST'])
def handle_remove_account():
    conn=connect_to_database()
    cursor=conn.cursor()
    customer_id=request.form['customer_id']

    try:
        cursor.execute(f"DELETE FROM cont_client WHERE id_client={customer_id}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Delete, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')

@app.route('/remove-personal-data',methods=['POST'])
def handle_remove_personal_info():
    conn=connect_to_database()
    cursor=conn.cursor()
    phone_pers_info=request.form['phone_pers_info']

    try:
        cursor.execute(f"DELETE FROM date_individ WHERE nr_telefon={phone_pers_info}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Delete, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')

@app.route('/update-account-verify',methods=['POST'])
def handle_update_account_verify():
    conn=connect_to_database()
    cursor=conn.cursor()
    customer_id=request.form['customer_id_upt']

    cursor.execute(f"SELECT true FROM cont_client WHERE id_client={customer_id}")
    if cursor.fetchone is None:
        return render_template('home.html',text=f'Invalid Update, Customer ID does not exist')
    
    cursor.execute(f"SELECT * FROM cont_client WHERE id_client={customer_id}")
    customer=cursor.fetchone()

    return render_template('update_account.html',customer=customer)

@app.route('/update-account-execute',methods=['POST'])
def handle_update_account_execute():
    conn=connect_to_database()
    cursor=conn.cursor()
    customer_id=request.form['customer_id_ex']
    phone_acc=request.form['phone_acc']
    email=request.form['email']

    try:
        cursor.execute(f"UPDATE cont_client SET nr_telefon={phone_acc},email='{email}' WHERE id_client={customer_id}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Update, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')