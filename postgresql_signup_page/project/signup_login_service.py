# signup_login_service.py
from flask import Flask, request, jsonify, render_template, url_for, session
from flask_bcrypt import Bcrypt
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Initialize Flask app and configurations
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Use a secure secret key for session management

# Use environment variables for database configuration for better security
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not all([db_username, db_password, db_host, db_port, db_name]):
    raise EnvironmentError("Database environment variables are not properly set.")

# Initialize bcrypt for password hashing
bcrypt = Bcrypt(app)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )

# Initialize database table
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

# Routes
@app.route('/')
def home():
    # Render the signup and login HTML page
    return render_template('signup_login.html')

@app.route('/signup', methods=['POST'])
def signup():
    # Parse JSON request data
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Username already exists"}), 400

    # Hash the password and insert the new user
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    # Parse JSON request data
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user by username
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not bcrypt.check_password_hash(user[0], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Store the username in the session
    session['username'] = username
    return jsonify({"message": "Login successful"}), 200

@app.route('/delete_user', methods=['POST'])
def delete_user():
    # Ensure the user is logged in
    if 'username' not in session:
        return jsonify({"error": "You must be logged in to delete your account"}), 403

    # Parse JSON request data
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Ensure the username matches the logged-in user
    if username != session['username']:
        return jsonify({"error": "You can only delete your own account"}), 403

    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch user by username
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if not user or not bcrypt.check_password_hash(user[0], password):
        cursor.close()
        connection.close()
        return jsonify({"error": "Invalid username or password"}), 401

    # Delete the user
    cursor.execute('DELETE FROM users WHERE username = %s', (username,))
    connection.commit()
    cursor.close()
    connection.close()

    # Clear the session
    session.pop('username', None)
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    # Call init_db to ensure database tables are created
    init_db()
    # Run the Flask app in debug mode for development
    app.run(debug=True)