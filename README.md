# Sunday Table

A sample restaurant ordering app with a vanilla JavaScript frontend, a Flask API, and SQLite order storage.

## Run locally

Requires Python 3.9 or newer.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The first run creates `instance/orders.db` automatically. Menu photos and web fonts are loaded from Unsplash and Google Fonts.

## API

- `GET /api/menu` returns the available menu items.
- `POST /api/orders` accepts `customer_name`, `table_number`, and an `items` array containing `menu_item_id` and `quantity`. Prices are looked up by the server; clients cannot set order prices.

## Tests

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```