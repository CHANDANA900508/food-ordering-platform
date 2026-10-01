from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
app = Flask(__name__)
# Database configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "orders_db")
DB_USER = os.getenv("DB_USER", "orders_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "orders_password")
DB_PORT = os.getenv("DB_PORT", "5432")
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            food_item VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP"
    })
# Create order
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400
    customer_name = data.get("customer_name")
    food_item = data.get("food_item")
    quantity = data.get("quantity")
    if not customer_name or not food_item or not quantity:
        return jsonify({
            "error": "customer_name, food_item and quantity are required"
        }), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders (customer_name, food_item, quantity)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (customer_name, food_item, quantity)
    )
    order_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Order created",
        "order_id": order_id
    }), 201
# Get orders
@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT id, customer_name, food_item, quantity
        FROM orders
        ORDER BY id
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(orders)
if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )