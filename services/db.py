import psycopg2
import os
from psycopg2.extras import RealDictCursor

# Database connection URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """Get a database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_db_cursor(db_connection):
    """Get a cursor for the given database connection."""
    return db_connection.cursor()

def create_user(email: str, password_hash: str, db_connection):
    """Create a new user in the database."""
    db_cursor = get_db_cursor(db_connection)
    insert_query = """
    INSERT INTO users (email, password_hash)
    VALUES (%s, %s);
    """
    db_cursor.execute(insert_query, (email, password_hash))
    db_connection.commit()
    db_cursor.close()

def get_user(email: str, db_connection):
    """Retrieve a user by email."""
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT id, email, password_hash
    FROM users
    WHERE email = %s;
    """
    db_cursor.execute(select_query, (email,))
    result = db_cursor.fetchone()
    db_cursor.close()
    return result  # Already a dictionary because of RealDictCursor

def insert_essay(content, feedback, teacher_id, assignment_id, db_connection) -> int:
    """Insert an essay and its generated feedback into the database."""
    query = """
    INSERT INTO essays (content, feedback, teacher_id, assignment_id)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    db_cursor = get_db_cursor(db_connection)
    db_cursor.execute(query, (content, feedback, teacher_id, assignment_id))
    essay_id = db_cursor.fetchone()["id"]
    db_connection.commit()
    db_cursor.close()
    return essay_id

def get_essay(teacher_id: int, assignment_id: int, db_connection):
    """Retrieve essays by teacher and assignment."""
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT content, feedback
    FROM essays
    WHERE teacher_id = %s AND assignment_id = %s;
    """
    db_cursor.execute(select_query, (teacher_id, assignment_id))
    results = db_cursor.fetchall()
    db_cursor.close()
    return results  # Returns a list of dictionaries with "content" and "feedback"


def create_assignment(title, teacher_id, db_connection, focus=None) -> int:
    """Create a new assignment."""
    query = """
    INSERT INTO assignments (title, teacher_id, focus)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    db_cursor = get_db_cursor(db_connection)
    db_cursor.execute(query, (title, teacher_id, focus))
    assignment_id = db_cursor.fetchone()["id"]
    db_connection.commit()
    db_cursor.close()
    return assignment_id


def get_assignment_by_id(assignment_id: int, db_connection):
    """Retrieve an assignment by its ID."""
    db_cursor = get_db_cursor(db_connection)
    select_query = """
    SELECT id, title, teacher_id, focus
    FROM assignments
    WHERE id = %s;
    """
    db_cursor.execute(select_query, (assignment_id,))
    result = db_cursor.fetchone()
    db_cursor.close()
    return result

def get_assignments_by_teacher(teacher_id, db_connection):
    """Retrieve all assignments for a given teacher."""
    query = """
    SELECT id, title, focus
    FROM assignments
    WHERE teacher_id = %s;
    """
    db_cursor = get_db_cursor(db_connection)
    db_cursor.execute(query, (teacher_id,))
    results = db_cursor.fetchall()
    db_cursor.close()
    return results
