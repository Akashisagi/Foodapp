import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("FO_DATABASE", BASE_DIR / "instance" / "orders.db"))

MENU = [
    {
        "id": 1,
        "name": "Burrata & stone fruit",
        "description": "Whipped basil oil, grilled sourdough, late-summer peaches.",
        "category": "Small plates",
        "price": 13.5,
        "image": "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?auto=format&fit=crop&w=900&q=85",
        "tag": "A guest favorite",
    },
    {
        "id": 2,
        "name": "Wild mushroom arancini",
        "description": "Crisp risotto, pecorino, and a bright lemon aioli.",
        "category": "Small plates",
        "price": 11.0,
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=900&q=85",
        "tag": "Vegetarian",
    },
    {
        "id": 3,
        "name": "Sunday tomato rigatoni",
        "description": "Slow-cooked tomato, parmesan, and torn garden basil.",
        "category": "Mains",
        "price": 19.0,
        "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85",
        "tag": "House-made pasta",
    },
    {
        "id": 4,
        "name": "Crispy chicken Milanese",
        "description": "Herb-crusted chicken, shaved fennel, caper butter.",
        "category": "Mains",
        "price": 24.0,
        "image": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=900&q=85",
        "tag": "From the kitchen",
    },
    {
        "id": 5,
        "name": "Olive oil cake",
        "description": "Soft citrus cake, macerated berries, crème fraîche.",
        "category": "Dessert",
        "price": 9.0,
        "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85",
        "tag": "Baked today",
    },
    {
        "id": 6,
        "name": "Blood orange spritz",
        "description": "Bitter orange, sparkling wine, a little rosemary.",
        "category": "Drinks",
        "price": 12.0,
        "image": "https://images.unsplash.com/photo-1513558161293-c0c7a9c7e8b9?auto=format&fit=crop&w=900&q=85",
        "tag": "Bright & bubbly",
    },
]

app = Flask(__name__)


@contextmanager
def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                table_number INTEGER NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                menu_item_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL
            );
            """
        )


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/menu")
def get_menu():
    return jsonify(MENU)


@app.post("/api/orders")
def create_order():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send order details as JSON."), 400

    customer_name = payload.get("customer_name")
    table_number = payload.get("table_number")
    items = payload.get("items")
    if not isinstance(customer_name, str) or not 2 <= len(customer_name.strip()) <= 80:
        return jsonify(error="Enter a name between 2 and 80 characters."), 400
    if isinstance(table_number, bool) or not isinstance(table_number, int) or not 1 <= table_number <= 50:
        return jsonify(error="Choose a table number from 1 to 50."), 400
    if not isinstance(items, list) or not items:
        return jsonify(error="Your order needs at least one item."), 400

    menu_by_id = {item["id"]: item for item in MENU}
    normalized_items = []
    for item in items:
        if not isinstance(item, dict):
            return jsonify(error="One of the order items is invalid."), 400
        item_id = item.get("menu_item_id")
        quantity = item.get("quantity")
        if (
            isinstance(item_id, bool)
            or not isinstance(item_id, int)
            or item_id not in menu_by_id
            or isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or not 1 <= quantity <= 20
        ):
            return jsonify(error="Check item selections and quantities (1 to 20)."), 400
        menu_item = menu_by_id[item_id]
        normalized_items.append((menu_item, quantity))

    total = round(sum(item["price"] * quantity for item, quantity in normalized_items), 2)
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO orders (customer_name, table_number, total) VALUES (?, ?, ?)",
            (customer_name.strip(), table_number, total),
        )
        order_id = cursor.lastrowid
        connection.executemany(
            """INSERT INTO order_items
               (order_id, menu_item_id, name, quantity, unit_price)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (order_id, item["id"], item["name"], quantity, item["price"])
                for item, quantity in normalized_items
            ],
        )

    return jsonify(order_id=order_id, total=total, message="Your order is on its way to the kitchen."), 201


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)