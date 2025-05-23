from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()
from db_config import get_db_connection
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import jwt
import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")

from functools import wraps


app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------------
# Route: Home
# -------------------------------
@app.route('/')
@cross_origin()
def home():
    return "🎓 AI Study Assistant API is running!"

# -------------------------------
# Route: Login a User
# -------------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token, 'name': user['name']}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401


# -------------------------------
# Route: Register a User
# -------------------------------
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO User (name, email, password) VALUES (%s, %s, %s)", 
               (name, email, hashed_password))
        conn.commit()
        return jsonify({"message": "✅ User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Route: View All Users (for testing)
# -------------------------------
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)
# -------------------------------
# Route: Add Study Material
# -------------------------------
@app.route('/add-material', methods=['POST'])
def add_material():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    subject = data.get('subject')
    topic = data.get('topic')
    url_or_path = data.get('url_or_path')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO StudyMaterial (title, description, subject, topic, url_or_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, subject, topic, url_or_path))
        conn.commit()
        return jsonify({"message": "✅ Study material added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Route: View All Study Materials
# -------------------------------
@app.route('/materials', methods=['GET'])
def get_materials():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StudyMaterial")
    materials = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(materials)

@app.route('/upload-material', methods=['POST'])
def upload_material():
    file = request.files['file']
    title = request.form.get('title')
    description = request.form.get('description')
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    author = request.form.get('author')

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO StudyMaterial (title, description, subject, topic, author, filename, url_or_path, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (title, description, subject, topic, author, filename, file_path, request.user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "✅ Study material uploaded successfully!"})


@app.route('/search-materials', methods=['GET'])
def search_materials():
    query = request.args.get('q', '')
    subject = request.args.get('subject')
    topic = request.args.get('topic')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT * FROM StudyMaterial WHERE 1=1"
    params = []

    if query:
        sql += " AND (title LIKE %s OR description LIKE %s)"
        params += [f"%{query}%", f"%{query}%"]

    if subject:
        sql += " AND subject = %s"
        params.append(subject)
    
    if topic:
        sql += " AND topic = %s"
        params.append(topic)

    cursor.execute(sql, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(results)

# -------------------------------
# Run Flask Server
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
