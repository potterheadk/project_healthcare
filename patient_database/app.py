# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from services.patient_service import (
    ensure_patient_records_table,
    add_patient_record,
    get_patient_records
)

app = Flask(__name__)
CORS(app)

# Initialize database table
ensure_patient_records_table()

@app.route('/add_record', methods=['POST'])
def add_record():
    """
    Add a patient record
    Example curl:
    curl -X POST http://localhost:5001/add_record \
        -F "username=turtle" \
        -F "record_name=Blood Test" \
        -F "record_data=Normal results" \
        -F "file=@/path/to/file.pdf"
    """
    try:
        username = request.form.get('username')
        record_name = request.form.get('record_name')
        record_data = request.form.get('record_data')
        file = request.files.get('file')  # Optional file

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
    """
    Get all records for a username
    Example curl:
    curl http://localhost:5001/get_records/turtle
    """
    try:
        response, status = get_patient_records(username)
        return jsonify(response), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(debug=True, port=port)