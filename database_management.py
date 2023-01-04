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
            DECLARE vechiul_nr_de_inchirieri INT;
            SELECT COUNT(*) INTO vechiul_nr_de_inchirieri FROM cerere WHERE id_masina = NEW.id_masina;
            IF vechiul_nr_de_inchirieri > 0 THEN
                SELECT MAX(data_retur) INTO ultima_data_retur FROM cerere WHERE id_masina = NEW.id_masina;
                IF NEW.data_inceput < ultima_data_retur THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Data invalida';
                END IF;
            END IF;
        END
    """)
    cursor.execute("""
        CREATE TRIGGER trg_cerere_data_inceput_before_update
        BEFORE UPDATE ON cerere
        FOR EACH ROW
        BEGIN
        DECLARE ultima_data_retur DATE;
        DECLARE vechiul_nr_de_inchirieri INT;
        SELECT COUNT(*) INTO vechiul_nr_de_inchirieri FROM cerere WHERE id_masina = NEW.id_masina;
        IF vechiul_nr_de_inchirieri > 0 THEN
            SELECT MAX(data_retur) INTO ultima_data_retur FROM cerere WHERE id_masina = NEW.id_masina;
            IF NEW.data_inceput < ultima_data_retur THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Data invalida';
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
            IF( CURRENT_TIMESTAMP()-NEW.data_nasterii <=18*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta minima 18 ani.';
            END IF;
            IF( CURRENT_TIMESTAMP()-NEW.data_nasterii >=75*365)
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
            IF( CURRENT_TIMESTAMP()-NEW.data_nasterii <=18*365)
            THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida varsta minima 18 ani.';
            END IF;
            IF( CURRENT_TIMESTAMP()-NEW.data_nasterii >=75*365)
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
                SET MESSAGE_TEXT = 'Data invalida ';
            END IF;
        END;
    """)
    cursor.execute("""
        CREATE TRIGGER trg_an_fabricatie_before_update
        BEFORE UPDATE ON masina 
        FOR EACH ROW 
        BEGIN
            IF( NEW.an_fabricatie >= CURRENT_TIMESTAMP() )
                THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Data invalida ';
            END IF;
        END;
    """)

    cursor.execute("""
    CREATE TRIGGER update_rating_masina_after_update
    AFTER UPDATE ON status_masina
    FOR EACH ROW
    BEGIN
    IF (NEW.stare_la_retur = 'ZGARIATA' and NEW.status='RETURNATA') THEN
        UPDATE cont_client
        SET rating = rating - 1
        WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
        and rating>4;
    END IF;
    IF (NEW.stare_la_retur = 'BUNA'and NEW.status='RETURNATA') THEN
            UPDATE cont_client
            SET rating = rating + 1
            WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
            and rating<10;
    END IF;
    IF (NEW.stare_la_retur = 'ACCIDENT'and NEW.status='RETURNATA') THEN
            UPDATE cont_client
            SET rating = rating - 4
            WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
            and rating>4;
    END IF;
    END
    """)
    cursor.execute("""
    CREATE TRIGGER update_rating_masina_after_insert
    AFTER INSERT ON status_masina
    FOR EACH ROW
    BEGIN
    IF (NEW.stare_la_retur = 'ZGARIATA' and NEW.status='RETURNATA') THEN
        UPDATE cont_client
        SET rating = rating - 1
        WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
        and rating>4;
    END IF;
    IF (NEW.stare_la_retur = 'BUNA'and NEW.status='RETURNATA') THEN
            UPDATE cont_client
            SET rating = rating + 1
            WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
            and rating<10;
    END IF;
    IF (NEW.stare_la_retur = 'ACCIDENT'and NEW.status='RETURNATA') THEN
            UPDATE cont_client
            SET rating = rating - 4
            WHERE id_client = (SELECT id_client FROM cerere WHERE id_masina = NEW.id_masina and NEW.data_retur_sm=data_retur)
            and rating>4;
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
    END;
    """)

    cursor.execute("""commit""")  