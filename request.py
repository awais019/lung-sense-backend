import sqlite3
from flask import Flask, jsonify, request, json
import uuid

app = Flask(__name__)

# Define the Student class
class Student:
    def __init__(self, firstname, lastname, department):
        self.id = uuid.uuid4().hex
        self.firstname = firstname
        self.lastname = lastname
        self.department = department

    def __str__(self):
        return f'id:{self.id} firstname: {self.firstname}; Lastname: {self.lastname}; Department: {self.department}'

# Set up SQLite database connection and create a "STUDENTS" table if it doesn't exist
def setup_database():
    c = sqlite3.connect("student.db").cursor()
    c.execute("CREATE TABLE IF NOT EXISTS STUDENTS("
              "id TEXT, firstname TEXT, lastname TEXT, department TEXT)")
    c.connection.close()

# Root route
@app.route('/', methods=['GET'])
def go_home():
    return 'Welcome to the Students API!'

# Get all students
@app.route('/getStudents', methods=['GET'])
def get_students():
    c = sqlite3.connect("student.db").cursor()
    c.execute("SELECT * FROM STUDENTS")
    data = c.fetchall()
    return jsonify(data)

# Get a student by ID
@app.route('/getStudentById/<student_id>', methods=['GET'])
def get_student_by_id(student_id):
    c = sqlite3.connect("student.db").cursor()
    c.execute("SELECT * FROM STUDENTS WHERE id=?", (student_id,))
    data = c.fetchone()
    return json.dumps(data)

# Add a new student
@app.route('/addStudent', methods=['POST'])
def add_student():
    setup_database()
    db = sqlite3.connect("student.db")
    c = db.cursor()
    student = Student(request.form["firstname"], request.form["lastname"], request.form["department"])
    c.execute("INSERT INTO STUDENTS VALUES(?,?,?,?)", (student.id, student.firstname, student.lastname, student.department))
    db.commit()
    data = c.lastrowid
    db.close()
    return json.dumps(data)

# Update a student
@app.route('/updateStudent/<student_id>', methods=['PUT'])
def update_student(student_id):
    db = sqlite3.connect("student.db")
    c = db.cursor()
    student = Student(request.form["firstname"], request.form["lastname"], request.form["department"])
    c.execute("UPDATE STUDENTS SET firstname = ?, lastname = ?, department = ? WHERE id=?", (student.firstname, student.lastname, student.department, student_id))
    db.commit()
    db.close()
    return json.dumps("Record was successfully updated")

# Delete a student by ID
@app.route('/deleteStudent/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    db = sqlite3.connect("student.db")
    c = db.cursor()
    c.execute("DELETE FROM STUDENTS WHERE id=?", (student_id,))
    db.commit()
    db.close()
    return json.dumps("Record was successfully deleted")

if __name__ == '__main__':
    setup_database()  # Ensure the database is set up when the app starts
    app.run(port=8888)
