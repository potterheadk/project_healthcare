import psycopg2
import os
from cryptography.fernet import Fernet
from flask_bcrypt import Bcrypt
import logging

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establish and return a database connection using environment variables.
    """
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def get_cipher():
    """
    Returns a Fernet cipher object initialized with the encryption key from the environment.
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise EnvironmentError("Encryption key is not set")
    return Fernet(key.encode())

def authenticate_user(username, password):
    """
    Authenticate a user by checking their credentials against the database.

    Args:
        username (str): The username.
        password (str): The password.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and bcrypt.check_password_hash(user[0], password):
            return True
        return False

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False

def get_patient_data(username):
    """
    Fetch and decrypt patient records for a given username.

    Args:
        username (str): The username to fetch records for.

    Returns:
        list: A list of decrypted records, each as a tuple
              (id, record_name, decrypted_data, file_type, created_at).
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, record_name, record_data, file_type, created_at 
            FROM patient_records 
            WHERE username = %s 
            ORDER BY created_at DESC
        ''', (username,))

        records = cursor.fetchall()
        cursor.close()
        connection.close()

        if not records:
            return []

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

        return decrypted_records

    except Exception as e:
        logger.error(f"Error fetching patient data: {str(e)}")
        return []
