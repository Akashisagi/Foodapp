import json
import tempfile
import unittest
from pathlib import Path

import app as restaurant_app


class RestaurantOrderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = restaurant_app.DATABASE_PATH
        restaurant_app.DATABASE_PATH = Path(self.temp_dir.name) / "test-orders.db"
        restaurant_app.initialize_database()
        self.client = restaurant_app.app.test_client()

    def tearDown(self):
        restaurant_app.DATABASE_PATH = self.original_database_path
        self.temp_dir.cleanup()

    def test_menu_is_served(self):
        response = self.client.get("/api/menu")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 6)

    def test_order_uses_server_prices_and_is_saved(self):
        response = self.client.post(
            "/api/orders",
            data=json.dumps({
                "customer_name": "  Sam  ",
                "table_number": 4,
                "items": [{"menu_item_id": 3, "quantity": 2}],
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["total"], 38.0)
        with restaurant_app.get_connection() as connection:
            order = connection.execute("SELECT customer_name, total FROM orders").fetchone()
            item = connection.execute("SELECT quantity FROM order_items").fetchone()
        self.assertEqual(order["customer_name"], "Sam")
        self.assertEqual(order["total"], 38.0)
        self.assertEqual(item["quantity"], 2)

    def test_rejects_invalid_order(self):
        response = self.client.post(
            "/api/orders",
            json={
                "customer_name": "Sam",
                "table_number": 4,
                "items": [{"menu_item_id": 999, "quantity": 1}],
            },
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()