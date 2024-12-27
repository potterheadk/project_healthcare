from flask import Flask, render_template, request, redirect, url_for, session, send_file
import psycopg2
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import io
from cryptography.fernet import Fernet
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
bcrypt = Bcrypt(app)
load_dotenv()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

def get_cipher():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise EnvironmentError("Encryption key is not set")
    return Fernet(key.encode())

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['username']
    password = request.form['password']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and bcrypt.check_password_hash(user[0], password):
            session['username'] = username
            cursor.close()
            connection.close()
            return redirect(url_for('dashboard'))
        
        cursor.close()
        connection.close()
        return render_template('login.html', error="Invalid username or password")
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template('login.html', error="An error occurred during login")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT id, record_name, record_data, file_type, created_at 
            FROM patient_records 
            WHERE username = %s 
            ORDER BY created_at DESC
        ''', (session['username'],))
        
        records = cursor.fetchall()
        cursor.close()
        connection.close()

        if not records:
            return render_template('dashboard.html', 
                                 username=session['username'],
                                 records=[])

        cipher = get_cipher()
        decrypted_records = []
        
        for record in records:
            try:
                decrypted_data = None
                if record[2]:  # if record_data exists
                    decrypted_data = cipher.decrypt(record[2].encode()).decode()
                
                decrypted_records.append((
                    record[0],        # id
                    record[1],        # record_name
                    decrypted_data,   # decrypted record_data
                    record[3],        # file_type
                    record[4]         # created_at
                ))
                
            except Exception as e:
                logger.error(f"Error decrypting record {record[0]}: {str(e)}")
                continue
        
        return render_template('dashboard.html',
                             username=session['username'],
                             records=decrypted_records)
                             
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return render_template('dashboard.html',
                             username=session['username'],
                             error=str(e),
                             records=[])

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