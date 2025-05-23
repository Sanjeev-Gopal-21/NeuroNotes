import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",  # ← change this
        database="study_assistant_db"
    )
