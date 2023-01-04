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
        CREATE TABLE date_individ (
            nr_telefon    CHAR(10) NOT NULL,
            nume          VARCHAR(15) NOT NULL,
            prenume       VARCHAR(25) NOT NULL,
            data_nasterii DATE NOT NULL,
            CHECK ( nr_telefon REGEXP '^[0][:7:3:2][0-9 ]*$' ),
            CHECK ( LENGTH(nume) >= 2 AND nume REGEXP '^[a-zA-Z ]*$' ),
            CHECK ( LENGTH(prenume) >= 2 AND prenume REGEXP '^[a-zA-Z ]*$' ),
            PRIMARY KEY (nr_telefon)
        )
    """)
    cursor.execute("""
        CREATE TABLE cont_client (
            id_client     INT NOT NULL AUTO_INCREMENT,
            rating        INT DEFAULT 10,
            nr_inchirieri INT,
            nr_telefon    CHAR(10) NOT NULL,
            email         VARCHAR(25),
            CHECK ( rating BETWEEN 0 AND 10 ),
            CHECK ( email REGEXP '[a-z0-9._%-]+@[a-z0-9._%-]+\.[a-z]{2,4}' ),
            UNIQUE INDEX cont_client__idx (nr_telefon),
            PRIMARY KEY (id_client),
            UNIQUE (email),
            FOREIGN KEY (nr_telefon) REFERENCES date_individ (nr_telefon)
        )
    """)
    cursor.execute("""
       CREATE TABLE masina (
            id_masina       INT NOT NULL AUTO_INCREMENT,
            tip_masina      VARCHAR(15) NOT NULL,
            an_fabricatie   DATE NOT NULL,
            culoare         VARCHAR(15) NOT NULL,
            pret_inchiriere INT NOT NULL,
            PRIMARY KEY (id_masina),
            CHECK (LENGTH(culoare) >= 2 AND culoare REGEXP '^[a-zA-Z ]*$'),
            CHECK (pret_inchiriere > 0)
        )
    """)
   
    cursor.execute("""
        CREATE TABLE cerere (
            id_cerere    INT NOT NULL AUTO_INCREMENT,
            data_inceput DATE NOT NULL,
            data_retur   DATE NOT NULL,
            id_client    INT NOT NULL,
            id_masina    INT NOT NULL,
            pret_total   INT NOT NULL,
            PRIMARY KEY (id_cerere),
            FOREIGN KEY (id_client) REFERENCES cont_client (id_client),
            FOREIGN KEY (id_masina) REFERENCES masina (id_masina)
        )
    """)

    cursor.execute("""
        CREATE TABLE lista_neagra (
            motiv_suspendare VARCHAR(35) NOT NULL,
            id_client        INT,
            PRIMARY KEY (motiv_suspendare),
            UNIQUE INDEX lista_neagra__idx (id_client),
            FOREIGN KEY (id_client) REFERENCES cont_client (id_client)
        )
    """)

    cursor.execute("""
        CREATE TABLE status_masina (
            id_masina        INT NOT NULL,
            status           VARCHAR(15) NOT NULL,
            stare_la_predare VARCHAR(20) DEFAULT 'BUNA',
            stare_la_retur   VARCHAR(20),
            data_retur_sm       DATE NOT NULL,
            UNIQUE INDEX status_masina__idx (id_masina),
            CHECK (status IN ('INCHIRIATA', 'RETURNATA')),
            CHECK (stare_la_retur IN ('ACCIDENT', 'BUNA', 'ZGARIATA')),
            FOREIGN KEY (id_masina) REFERENCES masina (id_masina) NOT DEFERRABLE
        )
    """)
 
    cursor.execute("commit")