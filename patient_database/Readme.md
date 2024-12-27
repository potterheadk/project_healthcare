# Patient Record Management Service

This service provides APIs for managing encrypted patient records, including the ability to add and retrieve records with optional file attachments.

---

## Setup Instructions

1. **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Install Dependencies**
    Make sure Python and `pip` are installed. Then, run:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**
    Create a `.env` file in the project root with the following variables:
    ```env
    DB_USERNAME=turtle_psql
    DB_PASSWORD=turtle6969
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=signup_login_psql
    ENCRYPTION_KEY=<your-generated-fernet-key>
    FLASK_PORT=5001
    ```

    - Replace `<your-generated-fernet-key>` with a valid Fernet key (see below).

4. **Generate Fernet Encryption Key**
    To generate the encryption key, run the following Python script:
    ```python
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    print(key.decode())
    ```
    Copy the output and set it as the `ENCRYPTION_KEY` in your `.env` file.

5. **Initialize the Database**
    Use the following commands to set up the PostgreSQL database:
    ```bash
    sudo -u postgres psql
    CREATE DATABASE signup_login_psql;
    CREATE USER turtle_psql WITH PASSWORD 'turtle6969';
    GRANT ALL PRIVILEGES ON DATABASE signup_login_psql TO turtle_psql;
    \q
    ```

6. **Run the Application**
    Start the Flask app:
    ```bash
    python app.py
    ```
    The application will run on `http://localhost:5001`.

---

## API Usage

### 1. Add Patient Record
- **Endpoint**: `/add_record`
- **Method**: `POST`
- **Description**: Adds a new patient record with optional file attachment.

#### Example `curl` Command:
```bash
curl -X POST http://localhost:5001/add_record \
    -F "username=turtle" \
    -F "record_name=Blood Test" \
    -F "record_data=Normal results" \
    -F "file=@/path/to/file.pdf"
```
- **Parameters**:
  - `username` (string): Patient's username.
  - `record_name` (string): Name of the record.
  - `record_data` (string, optional): Encrypted record data.
  - `file` (file, optional): File to be attached to the record.

#### Response:
- **Success**:
  ```json
  {
      "message": "Record added successfully",
      "record_id": 1
  }
  ```
- **Error**:
  ```json
  {
      "error": "<error-message>"
  }
  ```

### 2. Get Patient Records
- **Endpoint**: `/get_records/<username>`
- **Method**: `GET`
- **Description**: Retrieves all records for a specific username.

#### Example `curl` Command:
```bash
curl http://localhost:5001/get_records/turtle
```

#### Response:
- **Success**:
  ```json
  {
      "records": [
          {
              "id": 1,
              "record_name": "Blood Test",
              "record_data": "Normal results",
              "has_file": true,
              "file_type": "application/pdf",
              "created_at": "2024-12-27T12:34:56"
          }
      ]
  }
  ```
- **Error**:
  ```json
  {
      "error": "<error-message>"
  }
  ```

---

## Data Flow Explanation

1. **Adding a Record**:
    - Client sends a `POST` request to `/add_record` with required details and an optional file.
    - The `add_patient_record` function encrypts `record_data` using the Fernet key and stores the record and file (if any) in the database.

2. **Retrieving Records**:
    - Client sends a `GET` request to `/get_records/<username>`.
    - The `get_patient_records` function retrieves records from the database, decrypts the `record_data`, and returns the details to the client.

---

Feel free to reach out if you encounter any issues or need further clarification.

