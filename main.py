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
        return render_template('home.html',text='Tables already exist , Exception: '+str(e))
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
        return render_template('home.html',text='Data already inserted or tables do not exist , exception: '+str(e))
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
    customer_id=request.form['customer_id']

    cursor.execute(f"SELECT * FROM cont_client WHERE id_client={customer_id}")
    customer=cursor.fetchone()
    if customer is None:
        return render_template('home.html',text=f'Invalid Update, Customer ID : {customer_id} does not exist')
    return render_template('update_account.html',customer=customer)

@app.route('/update-account-execute',methods=['POST'])
def handle_update_account_execute():
    conn=connect_to_database()
    cursor=conn.cursor()
    customer_id=request.form['customer_id']
    email=request.form['email']

    try:
        cursor.execute(f"UPDATE cont_client SET email='{email}' WHERE id_client={customer_id}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Update, email does not respect format, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')

@app.route('/update-personal-data-verify',methods=['POST'])
def handle_update_personal_info_verify():
    conn=connect_to_database()
    cursor=conn.cursor()
    phone=request.form['phone']

    cursor.execute(f"SELECT * FROM date_individ WHERE nr_telefon={phone}")
    customer_info=cursor.fetchone()
    if customer_info is None:
        return render_template('home.html',text=f'Invalid Update, Phone Number : {phone} does not exist')
    return render_template('update_personal_data.html',customer_info=customer_info)

@app.route('/update-personal-data-execute',methods=['POST'])
def handle_update_personal_info_execute():
    conn=connect_to_database()
    cursor=conn.cursor()
    phone=request.form['phone']
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    birth_date=request.form['birth_date']

    try:
        cursor.execute(f"UPDATE date_individ SET nume='{last_name}', prenume='{first_name}', data_nasterii='{birth_date}' WHERE nr_telefon={phone}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Update, Exception: {e}')

    cursor.execute("commit")

    return redirect('/customers')

@app.route('/cars')
def handle_get_cars():
    conn=connect_to_database()
    cursor=conn.cursor()

    try:
        cursor.execute('SELECT * FROM masina')
        cars=cursor.fetchall()
        cursor.execute('SELECT * FROM status_masina')
        cars_status=cursor.fetchall()
    except Exception as e:
        return render_template('cars.html')
    return render_template('cars.html',cars=cars,cars_status=cars_status)

@app.route('/add-car',methods=['POST'])
def handle_add_car():
    conn=connect_to_database()
    cursor=conn.cursor()
    type=request.form['type']
    date=request.form['date']
    color=request.form['color']
    price=request.form['price']

    try:
        cursor.execute("INSERT INTO masina (tip_masina,an_fabricatie,culoare,pret_inchiriere) VALUES (%s,%s,%s,%s)",(type,date,color,price))
    except Exception as e:
        return render_template('home.html',text=f'Invalid Insert, Exception: {e}')

    cursor.execute("commit")
    
    return redirect('/cars')

@app.route('/remove-car',methods=['POST'])
def handle_remove_car():
    conn=connect_to_database()
    cursor=conn.cursor()
    car_id=request.form['car_id']

    try:
        cursor.execute(f"DELETE FROM masina WHERE id_masina={car_id}")
    except Exception as e:
        return render_template('home.html',text=f'Invalid Delete, Exception: {e}')

    cursor.execute("commit")

    return redirect('/cars')

@app.route('/update-car-verify',methods=['POST'])
def handle_update_car_verify():
    conn=connect_to_database()
    cursor=conn.cursor()
    car_id=request.form['car_id']

    cursor.execute(f"SELECT * FROM masina WHERE id_masina={car_id}")
    car=cursor.fetchone()
    if car is None:
        return render_template('home.html',text=f'Invalid Update, Car ID : {car_id} does not exist')
    return render_template('update_car.html',car=car)

@app.route('/add-car-status',methods=['POST'])
def handle_add_car_status():
    conn=connect_to_database()
    cursor=conn.cursor()
    car_id=request.form['car_id']
    status=request.form['status']
    return_date=request.form['return_date']

    try:
        cursor.execute("INSERT INTO status_masina (id_masina,status) VALUES (%s,%s)",(car_id,status))
    except Exception as e:
        return render_template('home.html',text=f'Invalid Insert, Exception: {e}')

    cursor.execute("commit")
    
    return redirect('/cars')
