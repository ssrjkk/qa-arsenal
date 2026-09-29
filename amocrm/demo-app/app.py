"""Demo Flask App для тестирования."""

import os
from datetime import datetime
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Config
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "amocrm"),
    "user": os.getenv("DB_USER", "user"),
    "password": os.getenv("DB_PASSWORD", "pass"),
}

# In-memory storage for demo (alternative to PostgreSQL)
users_db = {}
orders_db = {}
user_id_counter = 1
order_id_counter = 1


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route("/api/users", methods=["GET"])
def get_users():
    """Get all users."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY id")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"users": [dict(u) for u in users]})
    except Exception:
        return jsonify({"users": list(users_db.values())})


@app.route("/api/users", methods=["POST"])
def create_user():
    """Create new user."""
    global user_id_counter
    data = request.get_json()

    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email required"}), 400

    name = data["name"]
    email = data["email"]

    user = {"id": user_id_counter, "name": name, "email": email, "created_at": datetime.utcnow().isoformat()}

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id", (name, email))
        user["id"] = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        users_db[user_id_counter] = user
        user["id"] = user_id_counter
        user_id_counter += 1

    return jsonify({"user": user}), 201


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({"user": dict(user)})
        return jsonify({"error": "User not found"}), 404
    except Exception:
        user = users_db.get(user_id)
        if user:
            return jsonify({"user": user})
        return jsonify({"error": "User not found"}), 404


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update user."""
    data = request.get_json()

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if "name" in data:
            cur.execute("UPDATE users SET name = %s WHERE id = %s", (data["name"], user_id))
        if "email" in data:
            cur.execute("UPDATE users SET email = %s WHERE id = %s", (data["email"], user_id))

        conn.commit()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({"user": dict(user)})
        return jsonify({"error": "User not found"}), 404
    except Exception:
        user = users_db.get(user_id)
        if user:
            user.update(data)
            return jsonify({"user": user})
        return jsonify({"error": "User not found"}), 404


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete user."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        conn.close()

        if deleted:
            return jsonify({"deleted": True})
        return jsonify({"error": "User not found"}), 404
    except Exception:
        if user_id in users_db:
            del users_db[user_id]
            return jsonify({"deleted": True})
        return jsonify({"error": "User not found"}), 404


@app.route("/api/orders", methods=["POST"])
def create_order():
    """Create new order."""
    global order_id_counter
    data = request.get_json()

    if not data or "user_id" not in data or "amount" not in data:
        return jsonify({"error": "user_id and amount required"}), 400

    user_id = data["user_id"]
    amount = data["amount"]

    order = {
        "id": order_id_counter,
        "user_id": user_id,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (user_id, amount) VALUES (%s, %s) RETURNING id", (user_id, amount))
        order["id"] = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        orders_db[order_id_counter] = order
        order["id"] = order_id_counter
        order_id_counter += 1

    return jsonify({"order": order}), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Get all orders."""
    user_id = request.args.get("user_id")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if user_id:
            cur.execute("SELECT * FROM orders WHERE user_id = %s", (int(user_id),))
        else:
            cur.execute("SELECT * FROM orders")

        orders = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"orders": [dict(o) for o in orders]})
    except Exception:
        if user_id:
            orders = [o for o in orders_db.values() if o["user_id"] == int(user_id)]
        else:
            orders = list(orders_db.values())
        return jsonify({"orders": orders})


if __name__ == "__main__":
    import time

    # Try to initialize database (don't fail if no DB)
    max_retries = 5
    for i in range(max_retries):
        try:
            init_db()
            print("Database initialized!")
            break
        except Exception as e:
            print(f"DB not available ({i+1}/{max_retries}): {e}")
            time.sleep(1)

    app.run(host="0.0.0.0", port=8080, debug=False)
