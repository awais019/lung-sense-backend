import sqlite3
from flask import Flask, jsonify, request, json
import uuid
import tensorflow as tf
import pandas as pd
import scipy
import matplotlib.pyplot as plt
from keras import Model
from keras.layers import Conv2D, Dense, MaxPooling2D, Dropout, Flatten, GlobalAveragePooling2D
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau
from keras.layers import Input, Lambda, Dense, Flatten
from keras.models import Model
from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator, load_img
from keras.models import Sequential
import numpy as np
from fastapi import FastAPI, UploadFile
from glob import glob

app = Flask(__name__)

# Define the Student class


class Student:
    def __init__(self, firstname, lastname, password):
        self.id = uuid.uuid4().hex
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def __str__(self):
        return f'id:{self.id} firstname: {self.firstname}; Lastname: {self.lastname}; Password: {self.password}'

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
    student = Student(
        request.form["firstname"], request.form["lastname"], request.form["department"])
    c.execute("INSERT INTO STUDENTS VALUES(?,?,?,?)", (student.id,
              student.firstname, student.lastname, student.department))
    db.commit()
    data = c.lastrowid
    db.close()
    return json.dumps(data)

# Update a student


@app.route('/updateStudent/<student_id>', methods=['PUT'])
def update_student(student_id):
    db = sqlite3.connect("student.db")
    c = db.cursor()
    student = Student(
        request.form["firstname"], request.form["lastname"], request.form["department"])
    c.execute("UPDATE STUDENTS SET firstname = ?, lastname = ?, department = ? WHERE id=?",
              (student.firstname, student.lastname, student.department, student_id))
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

# Analyze an image


@app.route('/analyzeImage', methods=['POST'])
def analyzeImage():
    img = image.load_img('lun.jpeg', target_size=(224, 224))
    result = predict_image(img)
    print(result)
    json_result = {
        "result": "Image succesfully analyzed",
        "detection": result["class_name"],
    }
    return json_result


inception_v3 = tf.keras.applications.InceptionV3(
    weights='imagenet', include_top=False, input_shape=(224, 224, 3))

for layer in inception_v3.layers[:-15]:
    layer.trainable = False

x = inception_v3.output
x = Flatten()(x)
x = Dense(units=512, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(units=512, activation='relu')(x)
x = Dropout(0.3)(x)

output = Dense(units=4, activation='softmax')(x)
model = Model(inception_v3.input, output)

model.compile(optimizer='adam', loss='categorical_crossentropy',
              metrics=['accuracy'])

classes = ["AdenocarcinomaChest Lung Cancer", "Large cell carcinoma Lung Cancer",
           "NO Lung Cancer/ NORMAL", "Squamous cell carcinoma Lung Cancer"]


def predict_image(img):
    x = image.img_to_array(img)
    x = x / 255
    x = np.expand_dims(x, axis=0)
    img_data = preprocess_input(x)
    prediction = model.predict(img_data)
    class_index = np.argmax(prediction)
    class_name = classes[class_index]
    return {"class_name": class_name}


if __name__ == '__main__':
    setup_database()  # Ensure the database is set up when the app starts
    app.run(port=8888, debug=True)
