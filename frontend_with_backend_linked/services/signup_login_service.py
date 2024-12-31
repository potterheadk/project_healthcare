from flask_bcrypt import Bcrypt
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not all([db_username, db_password, db_host, db_port, db_name]):
    raise EnvironmentError("Database environment variables are not properly set.")

# Initialize bcrypt for password hashing
bcrypt = Bcrypt()

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )

# Database initialization
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

# Signup function
def signup(username, password):
    if not username or not password:
        return {"error": "Username and password are required"}, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return {"error": "Username already exists"}, 400

    # Hash the password and insert the new user
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User created successfully"}, 201

# Login function
def login(username, password):
    if not username or not password:
        return {"error": "Username and password are required"}, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user by username
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not bcrypt.check_password_hash(user[0], password):
        return {"error": "Invalid username or password"}, 401

    return {"message": "Login successful"}, 200

# Delete user function
def delete_user(username, password):
    if not username or not password:
        return {"error": "Username and password are required"}, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user by username
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if not user or not bcrypt.check_password_hash(user[0], password):
        cursor.close()
        connection.close()
        return {"error": "Invalid username or password"}, 401

    # Delete the user
    cursor.execute('DELETE FROM users WHERE username = %s', (username,))
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User deleted successfully"}, 200
