import psycopg2
import os
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_db_cursor(db_connection):
    db_cursor = db_connection.cursor()
    return db_cursor

def create_user(email: str, password_hash: str, db_connection):
    db_cursor = get_db_cursor(db_connection)
    insert_query = """
    INSERT INTO users (email, password_hash)
    VALUES (%s, %s);
    """
    db_cursor.execute(insert_query, (email, password_hash))
    db_connection.commit()
    db_cursor.close()

def get_user(email: str, db_connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT id, email, password_hash
    FROM users
    WHERE email = %s;
    """
    db_cursor.execute(select_query, (email,))
    result = db_cursor.fetchone()
    db_cursor.close()
    if not result:
        return None
    user = {
        "id": result['id'],
        "email": result['email'],
        "password_hash": result['password_hash']
    }
    return user

def insert_essay(essay: str, feedback: str, teacher_id: int, assignment_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)
    insert_query = """
    INSERT INTO essays (teacher_id, assignment_id, content, feedback)
    VALUES (%s, %s, %s, %s);
    """
    db_cursor.execute(insert_query, (teacher_id, assignment_id, essay, feedback))
    db_connection.commit()
    db_cursor.close()

def get_essay(teacher_id: int, assignment_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT content
    FROM essays
    WHERE teacher_id = %s AND assignment_id = %s;
    """
    db_cursor.execute(select_query, (teacher_id, assignment_id))
    results = db_cursor.fetchall()
    db_cursor.close()
    essays = [row['content'] for row in results]
    return essays

def create_assignment(title: str, teacher_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)
    insert_query = """
    INSERT INTO assignments (teacher_id, title)
    VALUES (%s, %s)
    RETURNING id;
    """
    db_cursor.execute(insert_query, (teacher_id, title))
    assignment_id = db_cursor.fetchone()['id']
    db_connection.commit()
    db_cursor.close()
    return assignment_id

def get_assignment(title: str, teacher_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT id, title
    FROM assignments
    WHERE teacher_id = %s AND title = %s;
    """
    db_cursor.execute(select_query, (teacher_id, title))
    result = db_cursor.fetchone()
    db_cursor.close()
    if not result:
        return None
    assignment = {
        "id": result['id'],
        "title": result['title']
    }
    return assignment
