from flask import Flask, request, jsonify
from db_config import get_db_connection
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------------
# Route: Home
# -------------------------------
@app.route('/')
def home():
    return "🎓 AI Study Assistant API is running!"

# -------------------------------
# Route: Register a User
# -------------------------------
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO User (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
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
    username = request.form.get('username')

    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Connect to DB to find user ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM User WHERE name = %s", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]

    # Save metadata to StudyMaterial table
    cursor.execute("""
        INSERT INTO StudyMaterial (title, description, subject, topic, author, filename, url_or_path, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (title, description, subject, topic, author, filename, file_path, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "✅ Study material uploaded successfully!"})


# -------------------------------
# Run Flask Server
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
