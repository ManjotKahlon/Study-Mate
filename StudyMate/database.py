
import sqlite3
from datetime import datetime

# Database file name
DB_NAME = "studymate.db"


# --------------------------------------------------
# 1. Connect to Database
# --------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# 2. Create Database Tables
# --------------------------------------------------

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # Study Tasks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)

    # Study Sessions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            duration INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# 3. Add New Study Task
# --------------------------------------------------

def add_task(subject, title, description, priority, due_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (subject, title, description, priority, due_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        subject,
        title,
        description,
        priority,
        due_date,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# 4. Get All Study Tasks
# --------------------------------------------------

def get_tasks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")

    tasks = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return tasks


# --------------------------------------------------
# 5. Update Task Status
# --------------------------------------------------

def update_task_status(task_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))

    conn.commit()
    conn.close()

    
# --------------------------------------------------
# Update Existing Study Task
# --------------------------------------------------

def edit_task(task_id, subject, title, description, priority, due_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET subject = ?,
            title = ?,
            description = ?,
            priority = ?,
            due_date = ?
        WHERE id = ?
    """, (
        subject,
        title,
        description,
        priority,
        due_date,
        task_id
    ))

    conn.commit()
    conn.close()



# --------------------------------------------------
# 6. Delete Study Task
# --------------------------------------------------

def delete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tasks WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


# --------------------------------------------------
# 7. Add Study Session
# --------------------------------------------------

def add_study_session(subject, duration, session_date, notes):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO study_sessions
        (subject, duration, session_date, notes)
        VALUES (?, ?, ?, ?)
    """, (subject, duration, session_date, notes))

    conn.commit()
    conn.close()


# --------------------------------------------------
# 8. Get All Study Sessions
# --------------------------------------------------

def get_study_sessions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM study_sessions
        ORDER BY session_date DESC, id DESC
    """)

    sessions = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return sessions


# --------------------------------------------------
# 9. Get Total Study Time
# --------------------------------------------------

def get_total_study_time():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(duration) FROM study_sessions
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total if total else 0


# --------------------------------------------------
# 10. Initialize Database
# --------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("StudyMate database created successfully!")


def edit_task(task_id, subject, title, description, priority, due_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET subject = ?,
            title = ?,
            description = ?,
            priority = ?,
            due_date = ?
        WHERE id = ?
    """, (
        subject,
        title,
        description,
        priority,
        due_date,
        task_id
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# Delete Study Session
# --------------------------------------------------

def delete_study_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM study_sessions
        WHERE id = ?
    """, (session_id,))

    conn.commit()
    conn.close()
