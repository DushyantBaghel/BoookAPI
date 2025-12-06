# backend/db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="7895056742",   # <-- yahan apna password daalo
        database="library_db",
        autocommit=False
    )
