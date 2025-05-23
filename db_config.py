import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user= os.getenv('db_user'),
        password= os.getenv('db_password'),
        database="study_assistant_db"
    )
