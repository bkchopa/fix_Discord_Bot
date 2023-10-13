import os
from flask import Flask, jsonify
import json
import main
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/greet', methods=['GET'])
def greet_api():
    users = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "age": 28
        },
        {
            "id": 3,
            "name": "Bob Brown",
            "email": "bob.brown@example.com",
            "age": 22
        }
    ]
    return jsonify({"message": "Hello from the API!", "users": users})