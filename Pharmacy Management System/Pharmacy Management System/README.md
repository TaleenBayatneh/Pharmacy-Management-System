# Pharmacy Management System

**Description:**

Simple pharmacy management web app built with Flask. Provides medicine inventory, orders, sales, subscriptions, prescriptions, user management, and reports. This workspace contains both admin (v1) and pharmacist (v2) views.

**Features:**

- Manage medicines (add / edit / stock warnings)
- Create and manage orders and sales
- Subscription & prescription handling
- User (pharmacist) management and roles
- Multiple report pages (12 report views)
- Two dashboard modes: admin (v1) and pharmacist (v2)

**Tech stack:**

- Python 3.x + Flask
- HTML, CSS, vanilla JS
- SQLite (or MySQL) via provided SQL dump

**Installation (local dev):**

1. Create and activate virtual env:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# or Command Prompt
.\.venv\Scripts\activate
```
2. Install dependencies (add `requirements.txt` if needed):

```bash
pip install flask
# add other deps as needed
```
3. Import the database:

```bash
# Use sqlite3 or your DB client against 1211305_1210520.sql
sqlite3 app.db < 1211305_1210520.sql
```

**Run (development):**

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
# or: python app.py
```

**Project structure (important files):**

- `app.py` — Flask app routes and entry point
- `1211305_1210520.sql` — DB schema + seed data
- `templates/` — Jinja templates (admin + pharmacist v2 pages)
- `static/css/` — CSS styles (many theme files; v2 pages use *_style.css)

**Routes & v1 ↔ v2 mapping**

The app uses two parallel UI sets: original admin (v1) and pharmacist (v2). Common routes are duplicated with a trailing `2` for pharmacist views.

- Dashboard: `/dashboard` → `/dashboard2`
- Medicine: `/medicien` → `/medicien2`
- Users: `/users` → `/users2`
- Customers: `/customer` → `/customer2`
- Orders: `/orders` → `/orders2`
- Sales: `/sales` → `/sales2`
- Add/Edit/Delete endpoints likewise append `2` for v2 (for example `/add_users` → `/add_users2`).

**Notes & gotchas**

- Browser autofill may populate the Add User form; inputs now include `autocomplete="off"` or `autocomplete="new-password"` where appropriate to prevent this.
- CSS file linking is important — some pages require `users.css` (not `users2.css`) to get the intended professional styling.
- Button/link styling may require `!important` to override browser defaults when using anchor tags as buttons.



