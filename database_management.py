import mysql.connector

def connect_to_database():
    conn=mysql.connector.connect(
        user='root',
        password='ajbdf243',
        database='rent_auto_project'
    )
    return conn

def create_tables_and_constraints():
    conn=connect_to_database()
    cursor=conn.cursor()

    cursor.execute("""
        create table date_individ (
            name varchar(25) not null
        )
    """)

    cursor.execute("""
        insert into date_individ values('Cosmin')
    """)

    cursor.execute("commit")