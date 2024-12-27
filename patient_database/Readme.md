# Patient Record Management Service

This document provides a detailed guide on how to use the `patient_service` module and its integration with a Flask-based API. This service enables secure storage, retrieval, and management of patient records in a PostgreSQL database.

---

## Prerequisites

1. **Environment Variables:** Ensure the following variables are set in your `.env` file:
    ```env
    DB_USERNAME=turtle_psql
    DB_PASSWORD=turtle6969
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=signup_login_psql
    ENCRYPTION_KEY=your_fernet_encryption_key
    FLASK_PORT=5001
    ```

2. **Database Initialization:** Set up the database by creating the `patient_records` table. Run the Flask app to automatically initialize the table, or execute the provided SQL commands in a PostgreSQL environment.

3. **Dependencies:** Install required Python libraries using:
    ```bash
    pip install psycopg2-binary cryptography python-dotenv flask flask-cors
    ```

---

## Module Functions

### 1. `ensure_patient_records_table()`
**Description:** Ensures the `patient_records` table exists in the database.

**Usage:** Automatically invoked during app startup. Can be called manually to reinitialize the table structure.

### 2. `add_patient_record(username, record_name, record_data=None, file=None)`
**Description:** Adds a patient record to the database. Supports optional file uploads.

**Inputs:**
- `username` (str): The patient's username.
- `record_name` (str): A descriptive name for the record.
- `record_data` (str, optional): Encrypted data related to the record.
- `file` (File, optional): A file to attach to the record.

**Output:**
- Success: `{"message": "Record added successfully", "record_id": record_id}` (HTTP 201)
- Failure: Error message with HTTP status code.

### 3. `get_patient_records(username)`
**Description:** Retrieves all records for a given username.

**Inputs:**
- `username` (str): The patient's username.

**Output:**
- Success: `{"records": [...records...]}` (HTTP 200)
- Failure: Error message with HTTP status code.

---

## Flask API Endpoints

### 1. **Add Record**
- **URL:** `/add_record`
- **Method:** `POST`
- **Example Curl Command:**
    ```bash
    curl -X POST http://localhost:5001/add_record \
        -F "username=turtle" \
        -F "record_name=Blood Test" \
        -F "record_data=Normal results" \
        -F "file=@/path/to/file.pdf"
    ```
- **Expected Response:**
    ```json
    {
        "message": "Record added successfully",
        "record_id": 1
    }
    ```

### 2. **Get Records**
- **URL:** `/get_records/<string:username>`
- **Method:** `GET`
- **Example Curl Command:**
    ```bash
    curl http://localhost:5001/get_records/turtle
    ```
- **Expected Response:**
    ```json
    {
        "records": [
            {
                "id": 1,
                "record_name": "Blood Test",
                "record_data": "Normal results",
                "has_file": true,
                "file_type": "application/pdf",
                "created_at": "2024-12-01T12:00:00"
            }
        ]
    }
    ```

---

## Data Flow

1. **Adding a Record:**
    - The client sends a `POST` request to `/add_record` with form data and an optional file.
    - The `add_patient_record` function encrypts the record data and stores it in the database.
    - If a file is provided, it is stored as binary data along with its MIME type.

2. **Retrieving Records:**
    - The client sends a `GET` request to `/get_records/<username>`.
    - The `get_patient_records` function fetches all records for the username from the database.
    - Record data is decrypted, and file presence and type are indicated in the response.

---

## Error Handling

- **Missing Required Fields:** Returns a 400 error with a descriptive message.
- **Encryption Key Issues:** Raises an `EnvironmentError` if the encryption key is not set.
- **Database Errors:** Returns a 500 error with the exception message.

---

## Running the Application

1. **Start the Flask App:**
    ```bash
    python app.py
    ```
2. **Access the Endpoints:** Use tools like `curl`, Postman, or any HTTP client to interact with the API.

---


