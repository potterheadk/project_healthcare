# service.py
import os
import psycopg2
import mimetypes
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

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

def ensure_patient_records_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_records (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            record_name VARCHAR(255) NOT NULL,
            record_data TEXT,
            file_data BYTEA,
            file_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    connection.commit()
    cursor.close()
    connection.close()

def add_patient_record(username, record_name, record_data=None, file=None):
    if not username or not record_name:
        return {"error": "Username and record name are required"}, 400
        
    try:
        # Handle file if provided
        file_data = None
        file_type = None
        if file:
            file_data = file.read()
            file_type = mimetypes.guess_type(file.filename)[0]

        # Encrypt record data if provided
        cipher = get_cipher()
        encrypted_data = cipher.encrypt(record_data.encode()).decode() if record_data else None

        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            INSERT INTO patient_records (username, record_name, record_data, file_data, file_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, record_name, encrypted_data, file_data, file_type))
        
        record_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "Record added successfully", "record_id": record_id}, 201

    except Exception as e:
        return {"error": str(e)}, 500

def get_patient_records(username):
    if not username:
        return {"error": "Username is required"}, 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT id, record_name, record_data, file_data, file_type, created_at
            FROM patient_records
            WHERE username = %s
            ORDER BY created_at DESC
        ''', (username,))
        
        records = cursor.fetchall()
        cursor.close()
        connection.close()

        if not records:
            return {"message": "No records found"}, 404

        cipher = get_cipher()
        results = []
        for record in records:
            record_dict = {
                "id": record[0],
                "record_name": record[1],
                "record_data": cipher.decrypt(record[2].encode()).decode() if record[2] else None,
                "has_file": bool(record[3]),
                "file_type": record[4],
                "created_at": record[5].isoformat()
            }
            results.append(record_dict)

        return {"records": results}, 200

    except Exception as e:
        return {"error": str(e)}, 500