from flask import Flask, request, jsonify, render_template, url_for, session
from services.signup_login_service import signup, login, delete_user, init_db

app = Flask(__name__)
app.secret_key = "w`yBr$5P3kQzkIa"

# Initialize database on app start
with app.app_context():
    init_db()

@app.route('/')
def home():
    # Render the signup and login HTML page
    return render_template('signup_login.html')

@app.route('/signup', methods=['POST'])
def api_signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    result, status = signup(username, password)
    return jsonify(result), status

@app.route('/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    result, status = login(username, password)
    return jsonify(result), status

@app.route('/delete_user', methods=['POST'])
def api_delete_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    result, status = delete_user(username, password)
    return jsonify(result), status

if __name__ == '__main__':
    app.run(debug=True)
