import mysql.connector

def connect_to_database():
    conn=mysql.connector.connect(
        user='root',
        password='ajbdf243',
        database='rent_auto_project'
    )
    return conn

def delete_tables():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
 
    cursor.execute("SHOW TRIGGERS")
    triggers = cursor.fetchall()
    
    # Iterate through the list of triggers and drop each one
    for trigger in triggers:
        trigger_name = trigger[0]
        cursor.execute(f"DROP TRIGGER {trigger_name}")

    cursor.execute("COMMIT")

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
            nr_inchirieri INT DEFAULT 0,
            nr_telefon    CHAR(10) NOT NULL,
            email         VARCHAR(45),
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
            pret_total   INT DEFAULT 0,
            PRIMARY KEY (id_cerere),
            FOREIGN KEY (id_client) REFERENCES cont_client (id_client),
            FOREIGN KEY (id_masina) REFERENCES masina (id_masina)
        )

    """)

    cursor.execute("""
        CREATE TABLE lista_neagra (
            motiv_suspendare VARCHAR(100) NOT NULL,
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
            stare_la_predare VARCHAR(20) DEFAULT 'GOOD CONDITION',
            stare_la_retur   VARCHAR(20) DEFAULT 'UNKNOWN',
            data_retur_sm       DATE NOT NULL,
            UNIQUE INDEX status_masina__idx (id_masina),
            CHECK (status IN ('RENTED', 'RETURNED')),
            CHECK (stare_la_retur IN ('UNKNOWN','ACCIDENT', 'GOOD CONDITION', 'SCRATCHED')),
            FOREIGN KEY (id_masina) REFERENCES masina (id_masina)
        )
    """)

    cursor.execute("""
        CREATE TRIGGER update_nr_inchirieri
        AFTER INSERT ON cerere
        FOR EACH ROW
        BEGIN
        UPDATE cont_client
        SET nr_inchirieri = nr_inchirieri + 1
        WHERE id_client = NEW.id_client;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_cerere_data_inceput_before_insert
        BEFORE INSERT ON cerere
        FOR EACH ROW
        BEGIN
            DECLARE ultima_data_retur DATE;
            DECLARE prima_data_inchiriere DATE;
            DECLARE vechiul_nr_de_inchirieri INT;
            SELECT COUNT(*) INTO vechiul_nr_de_inchirieri FROM cerere WHERE id_masina = NEW.id_masina;
            IF vechiul_nr_de_inchirieri > 0 THEN
                SELECT MAX(data_retur) INTO ultima_data_retur FROM cerere WHERE id_masina = NEW.id_masina;
                SELECT MIN(data_inceput) INTO prima_data_inchiriere FROM cerere WHERE id_masina = NEW.id_masina;
                IF (NEW.data_inceput > prima_data_inchiriere and NEW.data_inceput < ultima_data_retur) THEN 
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'bi:Data inserata nu indeplineste conditiile';
                END IF;
            END IF;
        END
    """)
  
    cursor.execute("""
        CREATE TRIGGER trg_cerere_id_client_before_insert
        BEFORE INSERT ON cerere 
        FOR EACH ROW 
        BEGIN
            DECLARE temp_var INT;
            SELECT COUNT(*) INTO temp_var FROM lista_neagra 
            WHERE lista_neagra.id_client = NEW.id_client;
            IF(temp_var=1 or temp_var > 1)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'ID-ul client se alfa in lista neagra';
            END IF;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_cerere_id_client_before_update
        BEFORE UPDATE ON cerere 
        FOR EACH ROW 
        BEGIN
            DECLARE temp_var INT;
            SELECT COUNT(*) INTO temp_var FROM lista_neagra 
            WHERE lista_neagra.id_client = NEW.id_client;
            IF(temp_var=1 or temp_var > 1)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'ID-ul client se alfa in lista neagra';
            END IF;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_data_nasterii_before_insert
        BEFORE INSERT ON date_individ 
        FOR EACH ROW 
        BEGIN
            IF( DATEDIFF(CURRENT_TIMESTAMP(),NEW.data_nasterii)  <=18*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta minima 18 ani.';
            END IF;
            IF( DATEDIFF(CURRENT_TIMESTAMP(),NEW.data_nasterii)  >=75*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta maxima 75 ani.';
            END IF;
        END
    """)

    cursor.execute("""
        CREATE TRIGGER trg_data_nasterii_before_update
        BEFORE INSERT ON date_individ 
        FOR EACH ROW 
        BEGIN
            IF( DATEDIFF(CURRENT_TIMESTAMP(),NEW.data_nasterii)  <=18*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta minima 18 ani.';
            END IF;
            IF( DATEDIFF(CURRENT_TIMESTAMP(),NEW.data_nasterii) >=75*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta maxima 75 ani.';
            END IF;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_an_fabricatie_before_insert 
        BEFORE INSERT ON masina 
        FOR EACH ROW 
        BEGIN
            IF( NEW.an_fabricatie >= CURRENT_TIMESTAMP() )
                THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida pentru anul fabricatiei';
            END IF;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_an_fabricatie_before_update
        BEFORE UPDATE ON masina 
        FOR EACH ROW 
        BEGIN
            IF( NEW.an_fabricatie >= CURRENT_TIMESTAMP() )
                THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida pentru anul fabricatiei';
            END IF;
        END
    """)

    cursor.execute("""
    CREATE TRIGGER update_rating_si_lista_cereri_after_update
    AFTER UPDATE ON status_masina
    FOR EACH ROW
    BEGIN
    DECLARE nr_inchirieri_masina INT;
    DECLARE prima_data_inchiriere DATE;
    DECLARE var_client INT;
    DECLARE var_rental_date DATE;

    SELECT COUNT(*) into nr_inchirieri_masina from cerere where id_masina=NEW.id_masina and data_inceput<NEW.data_retur_sm;
    SELECT MIN(data_inceput) into prima_data_inchiriere from cerere where id_masina=NEW.id_masina and data_inceput<NEW.data_retur_sm;
    IF(nr_inchirieri_masina>1) THEN
        DELETE from cerere where id_masina=NEW.id_masina and data_inceput>prima_data_inchiriere and data_inceput<NEW.data_retur_sm;
        UPDATE cerere SET pret_total= (datediff(NEW.data_retur_sm,data_inceput)*(select pret_inchiriere from masina where id_masina=NEW.id_masina)),
        data_retur = NEW.data_retur_sm where id_masina=NEW.id_masina and data_inceput=prima_data_inchiriere;
    ELSEIF (nr_inchirieri_masina=1) THEN
        UPDATE cerere
        SET data_retur = NEW.data_retur_sm,
        pret_total= (datediff(NEW.data_retur_sm,data_inceput)*(select pret_inchiriere from masina where id_masina=NEW.id_masina))
        WHERE id_masina = NEW.id_masina
        AND data_inceput = prima_data_inchiriere;
    END IF;
    SELECT id_client, data_inceput INTO var_client, var_rental_date FROM cerere WHERE id_masina = NEW.id_masina AND data_retur = NEW.data_retur_sm;
    IF (NEW.stare_la_retur = 'SCRATCHED' and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating - 1
        WHERE id_client = var_client
        and rating>4
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    IF (NEW.stare_la_retur = 'GOOD CONDITION'and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating + 1
        WHERE id_client = var_client
        and rating<10
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    IF (NEW.stare_la_retur = 'ACCIDENT'and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating - 4
        WHERE id_client = var_client
        and rating>4
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    END
    """)

    cursor.execute("""
    CREATE TRIGGER update_rating_si_lista_cereri_after_insert
    AFTER INSERT ON status_masina
    FOR EACH ROW
    BEGIN
    DECLARE nr_inchirieri_masina INT;
    DECLARE prima_data_inchiriere DATE;
    DECLARE var_client INT;
    DECLARE var_rental_date DATE;

    SELECT COUNT(*) into nr_inchirieri_masina from cerere where id_masina=NEW.id_masina and data_inceput<NEW.data_retur_sm;
    SELECT MIN(data_inceput) into prima_data_inchiriere from cerere where id_masina=NEW.id_masina and data_inceput<NEW.data_retur_sm;
    IF(nr_inchirieri_masina>1) THEN
        DELETE from cerere where id_masina=NEW.id_masina and data_inceput>prima_data_inchiriere and data_inceput<NEW.data_retur_sm;
        UPDATE cerere SET pret_total= (datediff(NEW.data_retur_sm,data_inceput)*(select pret_inchiriere from masina where id_masina=NEW.id_masina)),
        data_retur = NEW.data_retur_sm where id_masina=NEW.id_masina and data_inceput=prima_data_inchiriere;
    ELSEIF (nr_inchirieri_masina=1) THEN
        UPDATE cerere
        SET data_retur = NEW.data_retur_sm,
        pret_total= (datediff(NEW.data_retur_sm,data_inceput)*(select pret_inchiriere from masina where id_masina=NEW.id_masina))
        WHERE id_masina = NEW.id_masina
        AND data_inceput = prima_data_inchiriere;
    END IF;
    SELECT id_client, data_inceput INTO var_client, var_rental_date FROM cerere WHERE id_masina = NEW.id_masina AND data_retur = NEW.data_retur_sm;
    IF (NEW.stare_la_retur = 'SCRATCHED' and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating - 1
        WHERE id_client = var_client
        and rating>4
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    IF (NEW.stare_la_retur = 'GOOD CONDITION'and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating + 1
        WHERE id_client = var_client
        and rating<10
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    IF (NEW.stare_la_retur = 'ACCIDENT'and NEW.status='RETURNED') THEN
        UPDATE cont_client
        SET rating = rating - 4
        WHERE id_client = var_client
        and rating>4
        and var_rental_date = (SELECT data_inceput FROM cerere WHERE id_masina = NEW.id_masina and data_retur = NEW.data_retur_sm);
    END IF;
    END
    """)
    

    cursor.execute("""
    CREATE TRIGGER inserare_lista_neagra_after_update
    AFTER UPDATE ON cont_client
    FOR EACH ROW
    BEGIN
    IF (NEW.rating <= 4) THEN
        INSERT INTO lista_neagra (motiv_suspendare, id_client)
        VALUES ('rating <= 4', NEW.id_client);
    END IF;
    END;
    """)


    cursor.execute("""
    CREATE TRIGGER inserare_lista_neagra_after_insert
    AFTER INSERT ON cont_client
    FOR EACH ROW
    BEGIN
    IF (NEW.rating <= 4) THEN
        INSERT INTO lista_neagra (motiv_suspendare, id_client)
        VALUES ('rating <= 4', NEW.id_client);
    END IF;
    END
    """)

    cursor.execute("""commit""")  


def add_cerere(data_inceput, data_retur,id_client, id_masina):
    return f"""
        INSERT INTO cerere (id_cerere, data_inceput, data_retur, id_client, id_masina, pret_total)
        VALUES
        (NULL, '{data_inceput}', '{data_retur}', {id_client}, {id_masina},
        (SELECT DATEDIFF('{data_retur}', '{data_inceput}') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina={id_masina}))
    """

"""query = create_cerere('2020-03-20', '2020-03-25', 1)
cursor.execute(query)"""

def insert_values():
    conn=connect_to_database()
    cursor=conn.cursor()
    
    cursor.execute("""
        INSERT INTO masina (id_masina, tip_masina, an_fabricatie, culoare, pret_inchiriere) 
        VALUES
            (NULL, 'BMW', '2000-03-10', 'Brown', 100),
            (NULL, 'AUDI', '2008-05-05', 'Red', 95),
            (NULL, 'SCODA', '2010-02-01', 'Yellow', 110),
            (NULL, 'MERCEDES', '2005-04-10', 'Blue', 75),
            (NULL, 'TESLA', '2015-12-25', 'Black', 150),
            (NULL, 'DACIA', '2007-10-27', 'Green', 65),
            (NULL, 'PEUGEOT', '2013-03-10', 'Pink', 80)
    """)

    cursor.execute("""
        INSERT INTO date_individ (nr_telefon, nume, prenume, data_nasterii)
        VALUES
            ('0722222222', 'Ion', 'Ion', '1980-03-10'),
            ('0722222232', 'Ionut', 'Ion', '1970-03-27'),
            ('0722222252', 'Alex', 'Ion', '1985-10-10'),
            ('0722222262', 'Cosmin', 'Alex', '1981-11-11'),
            ('0722222272', 'Danut', 'Ion', '1994-05-15'),
            ('0722222282', 'Alt', 'Ion', '1999-03-16'),
            ('0722333282', 'Ion', 'Rating', '1999-03-16'),
            ('0742333282', 'Lista', 'Neagra', '1999-03-16')
    """)

    cursor.execute("""
        INSERT INTO cont_client (id_client, rating, nr_inchirieri, nr_telefon, email)
        VALUES
            (NULL, DEFAULT, 0, '0722222222', 'ion.ion@gmail.com'),
            (NULL, DEFAULT, 0, '0722222232', 'ionut.ion@gmail.com'),
            (NULL, DEFAULT, 0, '0722222252', 'alex.ion@gmail.com'),
            (NULL, DEFAULT, 0, '0722222262', 'cosmin.alex@gmail.com'),
            (NULL, DEFAULT, 0, '0722222272', 'danut.ion@gmail.com'),
            (NULL, DEFAULT, 0, '0722222282', 'alt.ion@gmail.com')
    """)

    cursor.execute("""
        INSERT INTO lista_neagra(motiv_suspendare,id_client) VALUES
        ('HAD AN ACCIDENT',1),
        ('INAPPROPRIATE BEHAVIOR',4)
    """)

    cursor.execute("""
        INSERT INTO cerere (id_cerere, data_inceput, data_retur, id_client, id_masina, pret_total)
        VALUES
        (NULL, '2020-03-20', '2020-03-25', 2, 1,
        (SELECT DATEDIFF('2020-03-25', '2020-03-20') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina=1)),
        (NULL, '2020-03-26', '2020-03-28', 3, 1,
        (SELECT DATEDIFF('2020-03-28', '2020-03-26') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina=1)),
        (NULL, '2020-03-27', '2020-03-30', 6, 4,
        (SELECT DATEDIFF('2020-03-30', '2020-03-27') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina=4)),
        (NULL, '2020-03-27', '2020-03-30', 5, 3,
        (SELECT DATEDIFF('2020-03-30', '2020-03-27') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina=3)),
        (NULL, '2020-04-01', '2020-04-05', 6, 4,
        (SELECT DATEDIFF('2020-04-05', '2020-04-01') FROM DUAL)*(SELECT pret_inchiriere FROM masina WHERE id_masina=4))
    """)

    cursor.execute("""
        INSERT INTO status_masina (id_masina, status, stare_la_predare, stare_la_retur, data_retur_sm)
        VALUES
        (1, 'RENTED', DEFAULT, DEFAULT, '2020-03-25'),
        (3, 'RENTED', DEFAULT, DEFAULT, '2020-03-30'),
        (4, 'RENTED', DEFAULT, DEFAULT, '2020-04-05')
    """)

    cursor.execute("""commit""")

