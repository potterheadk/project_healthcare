# Flask Signup, Login, and Delete Module Documentation

## Overview
This module provides functionalities for user authentication and management, including signing up, logging in, and deleting users. It uses Flask for the web framework, Flask-Bcrypt for password hashing, and PostgreSQL as the database.

## Key Components

### 1. **Environment Variables**
The module requires specific environment variables to connect to the PostgreSQL database. These variables should be stored in a `.env` file:

```plaintext
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
```
Ensure all variables are properly set, or an error will be raised during initialization.

### 2. **Functions**

#### `init_db()`
Initializes the database by creating the necessary `users` table if it doesn't already exist.

#### `get_db_connection()`
Establishes and returns a connection to the PostgreSQL database.

#### `signup(username, password)`
- **Description**: Registers a new user by storing their hashed password.
- **Parameters**:
  - `username`: The username for the new account (string).
  - `password`: The plaintext password for the new account (string).
- **Returns**: JSON response with a success or error message and an HTTP status code.

#### `login(username, password)`
- **Description**: Authenticates a user by verifying their credentials.
- **Parameters**:
  - `username`: The username of the account (string).
  - `password`: The plaintext password of the account (string).
- **Returns**: JSON response with a success or error message and an HTTP status code.

#### `delete_user(username, password)`
- **Description**: Deletes a user account after verifying credentials.
- **Parameters**:
  - `username`: The username of the account to delete (string).
  - `password`: The plaintext password of the account (string).
- **Returns**: JSON response with a success or error message and an HTTP status code.

### 3. **Flask Integration**
The module integrates seamlessly with Flask. The following routes are available:

#### `/` (GET)
- **Description**: Renders the `signup_login.html` template.

#### `/signup` (POST)
- **Description**: Endpoint to register a new user.
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "example_password"
  }
  ```
- **Response**:
  - Success: `{"message": "User created successfully"}`
  - Failure: `{"error": "Username already exists"}`

#### `/login` (POST)
- **Description**: Endpoint to log in a user.
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "example_password"
  }
  ```
- **Response**:
  - Success: `{"message": "Login successful"}`
  - Failure: `{"error": "Invalid username or password"}`

#### `/delete_user` (POST)
- **Description**: Endpoint to delete a user account.
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "example_password"
  }
  ```
- **Response**:
  - Success: `{"message": "User deleted successfully"}`
  - Failure: `{"error": "Invalid username or password"}`

## Setting Up the Project

1. **Install Dependencies**:
   ```bash
   pip install flask flask-bcrypt psycopg2 python-dotenv
   ```

2. **Create a `.env` File**:
   Populate the file with the required database credentials.

3. **Initialize the Database**:
   Ensure the database server is running and accessible. The `init_db()` function will create the necessary table when the Flask app starts.

4. **Run the Flask App**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open a web browser and navigate to `http://localhost:5000`.

## Database Initialization Commands
Use the following commands to set up the PostgreSQL database on a Linux system:

1. **Switch to PostgreSQL User**:
   ```bash
   sudo -i -u postgres
   ```

2. **Access PostgreSQL Command Line Interface**:
   ```bash
   psql
   ```

3. **Create a New Database**:
   ```sql
   CREATE DATABASE signup_login_psql;
   ```

4. **Create a New User**:
   ```sql
   CREATE USER turtle_psql WITH PASSWORD 'turtle6969';
   ```

5. **Grant Privileges to the User**:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE signup_login_psql TO turtle_psql;
   ```

6. **Exit PostgreSQL**:
   ```bash
   \q
   exit
   ```

7. **Test Database Connection**:
   Use the `psql` command or your application to verify the connection using the environment variables:
   ```plaintext
   DB_USERNAME=turtle_psql
   DB_PASSWORD=turtle6969
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=signup_login_psql
   ```

## File Structure
```plaintext
project/
├── app.py                    # Main Flask application
├── services/
│   └── signup_login_service.py  # Authentication module
├── templates/
│   └── signup_login.html     # Frontend template
├── .env                      # Environment variables
└── requirements.txt          # Python dependencies
```

## Security Notes
- Use a strong `SECRET_KEY` for the Flask app to secure sessions.
- Ensure database credentials in the `.env` file are not exposed in version control.
- Use HTTPS in production to secure data transmission.

## Future Improvements
- Add token-based authentication (e.g., JWT) for stateless sessions.
- Implement rate limiting to prevent brute force attacks.
- Provide detailed logging for debugging and monitoring.

