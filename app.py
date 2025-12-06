# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

def _row_to_dict(cursor, row):
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))

@app.route("/books", methods=["GET"])
def get_books():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        books = [_row_to_dict(cursor, r) for r in rows]
        cursor.close(); conn.close()
        return jsonify(books), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/")
def home():
    return jsonify({"message": "Library API is running"}), 200


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        row = cursor.fetchone()
        if row is None:
            cursor.close(); conn.close()
            return jsonify({"error":"Book not found"}), 404
        book = _row_to_dict(cursor, row)
        cursor.close(); conn.close()
        return jsonify(book), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(force=True)
    title = data.get("title")
    author = data.get("author")
    year = data.get("year", None)
    available = data.get("available", True)

    if not title or not author:
        return jsonify({"error":"title and author required"}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO books (title, author, year, available) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (title, author, year, available))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close(); conn.close()
        return jsonify({"message":"Book created","id": new_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/books/<int:book_id>", methods=["PUT"])
def replace_book(book_id):
    data = request.get_json(force=True)
    title = data.get("title")
    author = data.get("author")
    year = data.get("year", None)
    available = data.get("available", True)

    if not title or not author:
        return jsonify({"error":"title and author required"}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
        if cursor.fetchone() is None:
            cursor.close(); conn.close()
            return jsonify({"error":"Book not found"}), 404

        sql = "UPDATE books SET title=%s, author=%s, year=%s, available=%s WHERE id=%s"
        cursor.execute(sql, (title, author, year, available, book_id))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"message":"Book replaced"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
        if cursor.fetchone() is None:
            cursor.close(); conn.close()
            return jsonify({"error":"Book not found"}), 404

        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"message":"Book deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
