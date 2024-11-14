import pyodbc
from sqlite3 import Connection

def get_db_connection():
    connection_str = (
        "DRIVER={PostgreSQL};"
        "DATABASE=mydatabase;"
        "UID=myuser;"
        "PWD=mypassword;"
        "SERVER=db;"
        "PORT=5432;"
    )
    conn = pyodbc.connect(connection_str)
    return conn


def get_db_cursor(db_connection):
    db_cursor = db_connection.cursor()
    return db_cursor

def create_user(email: str, password_hash: str, db_connection: Connection):
    db_cursor = get_db_cursor(db_connection)
    insert_query = f"""
    INSERT INTO users (email, password_hash)
    VALUES (?, ?);
    """
    db_cursor.execute(insert_query, [email, password_hash])
    db_connection.commit()
    db_cursor.close()

def get_user(email: str, db_connection: Connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = f"""
    SELECT id, email, password_hash
    FROM users
    WHERE email = ?;
    """
    results = db_cursor.execute(select_query, email).fetchone()
    if not results:
        return None
    user = {
        "id": results.id,
        "email": results.email,
        "password_hash": results.password_hash
    }
    return user

def insert_essay(essay: str, feedback: str, teacher_id: int, assignment_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)

    insert_query = """
    INSERT INTO essays (teacher_id, assignment_id, content, feedback)
    VALUES (?, ?, ?, ?);
    """

    # Pass the actual values as parameters
    db_cursor.execute(insert_query, (teacher_id, assignment_id, essay, feedback))

    db_connection.commit()
    db_cursor.close()

def get_essay(teacher_id: int, assignment_id: int, db_connection: Connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = f"""
    SELECT content
    FROM essays
    WHERE teacher_id = {teacher_id} AND assignment_id = {assignment_id};
    """
    results = db_cursor.execute(select_query).fetchall()
    essays = []
    for row in results:
        essays.append(row.content)
    return essays

def create_assignment(title: str, teacher_id: int, db_connection: Connection):
    db_cursor = get_db_cursor(db_connection)
    insert_query = f"""
    INSERT INTO assignments (teacher_id, title)
    VALUES (?, ?)
    RETURNING id;
    """
    id = db_cursor.execute(insert_query, [teacher_id, title]).fetchone().id
    db_connection.commit()
    db_cursor.close()
    return id

def get_assignment(title: str, teacher_id: int, db_connection: Connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = f"""
    SELECT id, title
    FROM assignments
    WHERE teacher_id = ? AND title = ?;
    """
    result = db_cursor.execute(select_query, [teacher_id, title]).fetchone()
    if not result:
        return None
    assignment = {
        "id": result.id,
        "title": result.title
    }
    return assignment