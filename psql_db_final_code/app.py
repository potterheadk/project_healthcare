from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
import psycopg2
import logging
import io
from services.patient_service import (
    ensure_patient_records_table,
    add_patient_record,
    get_patient_records
)
from services.get_patient_data import get_patient_data, get_db_connection

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
bcrypt = Bcrypt(app)
CORS(app)

# Logging configuration
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Database configuration
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not all([db_username, db_password, db_host, db_port, db_name]):
    raise EnvironmentError("Database environment variables are not properly set.")

# Initialize database tables
def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL
        )
    ''')
    
    # Create patient records table
    ensure_patient_records_table()
    
    connection.commit()
    cursor.close()
    connection.close()

# Initialize database on app start
with app.app_context():
    init_db()

# Authentication Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup_login.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check if username exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Username already exists"}), 400
    
    # Create new user
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)',
                  (username, password_hash))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if user and bcrypt.check_password_hash(user[0], password):
        session['username'] = username
        return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    password = data.get('password')
    
    if not password:
        return jsonify({"error": "Password required"}), 400
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT password_hash FROM users WHERE username = %s',
                  (session['username'],))
    user = cursor.fetchone()
    
    if not user or not bcrypt.check_password_hash(user[0], password):
        cursor.close()
        connection.close()
        return jsonify({"error": "Invalid password"}), 401
    
    cursor.execute('DELETE FROM users WHERE username = %s', (session['username'],))
    connection.commit()
    cursor.close()
    connection.close()
    
    session.pop('username', None)
    return jsonify({"message": "User deleted successfully"}), 200

# Patient Record Routes
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    records = get_patient_data(session['username'])
    return render_template('dashboard.html',
                         username=session['username'],
                         records=records)

@app.route('/add_record', methods=['POST'])
def add_record():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        username = session['username']
        record_name = request.form.get('record_name')
        record_data = request.form.get('record_data')
        file = request.files.get('file')
        
        response, status = add_patient_record(
            username=username,
            record_name=record_name,
            record_data=record_data,
            file=file
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_records/<string:username>', methods=['GET'])
def get_records(username):
    if 'username' not in session or session['username'] != username:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        response, status = get_patient_records(username)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<int:record_id>')
def download_file(record_id):
    if 'username' not in session:
        return redirect(url_for('home'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT file_data, file_type, record_name
            FROM patient_records
            WHERE id = %s AND username = %s
        ''', (record_id, session['username']))
        record = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if record and record[0]:
            return send_file(
                io.BytesIO(record[0]),
                mimetype=record[1],
                as_attachment=True,
                download_name=f"{record[2]}.{record[1].split('/')[-1]}"
            )
        return "File not found", 404
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return "Error downloading file", 500

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=5002, debug=True)