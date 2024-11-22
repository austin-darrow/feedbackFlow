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

def insert_essay(writing_sample, feedback, teacher_id, assignment_id, db_connection):
    query = """
    INSERT INTO essays (writing_sample, feedback, teacher_id, assignment_id)
    VALUES (?, ?, ?, ?)
    """
    db_connection.execute(query, (writing_sample, feedback, teacher_id, assignment_id))
    db_connection.commit()

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

def create_assignment(title, teacher_id, db_connection, focus=None):
    query = "INSERT INTO assignments (title, teacher_id, focus) VALUES (?, ?, ?)"
    cursor = db_connection.execute(query, (title, teacher_id, focus))
    db_connection.commit()
    return cursor.lastrowid

def get_assignment_by_id(assignment_id: int, db_connection):
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT id, title, teacher_id, focus
    FROM assignments
    WHERE id = %s;
    """
    db_cursor.execute(select_query, (assignment_id,))
    result = db_cursor.fetchone()
    db_cursor.close()
    if not result:
        return None
    assignment = {
        "id": result['id'],
        "title": result['title'],
        "teacher_id": result['teacher_id'],
        "focus": result['focus']
    }
    return assignment


def get_assignments_by_teacher(teacher_id, db_connection):
    query = "SELECT id, title, focus FROM assignments WHERE teacher_id = ?"
    return db_connection.execute(query, (teacher_id,)).fetchall()
