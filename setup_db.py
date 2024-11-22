from services import db
import time

def drop_db_tables():
    time.sleep(3)
    db_connection = db.get_connection()
    db_cursor = db_connection.cursor()

    drop_table_query = """
    DROP TABLE IF EXISTS essays;
    DROP TABLE IF EXISTS assignments;
    DROP TABLE IF EXISTS users;
    """

    db_cursor.execute(drop_table_query)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()

def init_db():
    # drop_db_tables()
    db_connection = db.get_connection()
    db_cursor = db_connection.cursor()

    create_user_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    db_cursor.execute(create_user_table_query)
    db_connection.commit()

    create_assignment_table_query = """
    CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY,
        teacher_id INTEGER REFERENCES users (id) NOT NULL,
        title TEXT NOT NULL,
        focus TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    db_cursor.execute(create_assignment_table_query)
    db_connection.commit()

    create_essay_table_query = """
    CREATE TABLE IF NOT EXISTS essays (
        id SERIAL PRIMARY KEY,
        teacher_id INTEGER REFERENCES users (id) NOT NULL,
        assignment_id INTEGER REFERENCES assignments (id) NOT NULL,
        content TEXT NOT NULL,
        feedback TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    db_cursor.execute(create_essay_table_query)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()
