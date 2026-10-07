# Sunday Table

A sample restaurant ordering app with a vanilla JavaScript frontend, a Flask API, and MySQL order storage.

## Run locally

Requires Python 3.9 or newer and MySQL 8.0 or newer. Create the app database first:

```sql
CREATE DATABASE fo_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set the MySQL connection values in the environment before running the app. Defaults are shown below; set `MYSQL_PASSWORD` to the password for `MYSQL_USER`.

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your-password"
$env:MYSQL_DATABASE = "fo_app"
```

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The app creates its `orders` and `order_items` tables when the first valid order is submitted. Menu photos and web fonts are loaded from Unsplash and Google Fonts.

## API

- `GET /api/menu` returns the available menu items.
- `POST /api/orders` accepts `customer_name`, `table_number`, and an `items` array containing `menu_item_id` and `quantity`. Prices are looked up by the server; clients cannot set order prices.

## Tests

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

Tests use a temporary SQLite database. To explicitly use SQLite locally instead of MySQL, set `FO_DATABASE` to a database file path.