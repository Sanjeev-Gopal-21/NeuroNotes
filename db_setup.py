import mysql.connector

# Replace these with your own MySQL login credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',  # change this
    'database': 'study_assistant_db'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS StudyMaterial (
        material_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        subject VARCHAR(100) NOT NULL,
        topic VARCHAR(100) NOT NULL,
        url_or_path TEXT,
        date_added DATE DEFAULT CURRENT_DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AIQueryLog (
        query_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        question TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS WebScrapedContent (
        content_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        link TEXT NOT NULL,
        source VARCHAR(255),
        scraped_on DATE DEFAULT CURRENT_DATE
    )
    """)

    print("✅ Tables created successfully!")

except mysql.connector.Error as err:
    print(f"❌ Error: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
