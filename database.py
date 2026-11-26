import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("students.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL UNIQUE,
                department TEXT NOT NULL,
                year TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                marks INTEGER NOT NULL CHECK(marks >= 0 AND marks <= 100),
                UNIQUE(student_id, subject),
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)

def add_student(name, roll_number, department, year):
    with connect() as con:
        con.execute("INSERT INTO students(name, roll_number, department, year) VALUES (?, ?, ?, ?)",
                    (name, roll_number, department, year))

def get_students():
    with connect() as con:
        rows = con.execute("SELECT * FROM students ORDER BY name").fetchall()
        return [dict(r) for r in rows]

def update_student(student_id, name, department, year):
    with connect() as con:
        con.execute("UPDATE students SET name=?, department=?, year=? WHERE id=?",
                    (name, department, year, student_id))

def delete_student(student_id):
    with connect() as con:
        con.execute("DELETE FROM marks WHERE student_id=?", (student_id,))
        con.execute("DELETE FROM students WHERE id=?", (student_id,))

def save_marks(student_id, marks):
    with connect() as con:
        for subject, value in marks.items():
            con.execute("""
                INSERT INTO marks(student_id, subject, marks) VALUES (?, ?, ?)
                ON CONFLICT(student_id, subject) DO UPDATE SET marks=excluded.marks
            """, (student_id, subject, int(value)))

def get_marks(student_id):
    with connect() as con:
        rows = con.execute("SELECT subject, marks FROM marks WHERE student_id=? ORDER BY subject",
                           (student_id,)).fetchall()
        return [dict(r) for r in rows]

def get_all_results():
    with connect() as con:
        rows = con.execute("""
            SELECT s.id, s.name, s.roll_number,
                   SUM(m.marks) AS total,
                   COUNT(m.id) * 100 AS out_of,
                   ROUND(100.0 * SUM(m.marks) / (COUNT(m.id) * 100), 2) AS percentage
            FROM students s
            JOIN marks m ON s.id = m.student_id
            GROUP BY s.id
            ORDER BY percentage DESC
        """).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            p = item["percentage"]
            item["grade"] = ("A+" if p >= 90 else "A" if p >= 80 else "B" if p >= 70
                             else "C" if p >= 60 else "D" if p >= 50 else "F")
            results.append(item)
        return results

def get_student_report(student_id):
    with connect() as con:
        student = con.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        if not student:
            return None
        marks = con.execute("SELECT subject, marks FROM marks WHERE student_id=? ORDER BY subject",
                            (student_id,)).fetchall()
        return {"student": dict(student), "marks": [dict(r) for r in marks]}
