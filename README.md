# Cosmetic Product Management System

Full-stack Django application for tracking cosmetic inventories, monitoring expiry status, and analyzing usage patterns. Built for SDSC5003 Track 1: Database Application Development.

## Features

- **Inventory Management:** CRUD operations for brands, categories, and cosmetic products with image uploads and user ownership.
- **Expiration Analytics:** Automatic status calculation (`good/soon/urgent/expired`) plus expiring-products dashboard.
- **Advanced Filtering:** Search by keyword, status, and category with server-side pagination (10 rows per page).
- **Multi-User Isolation:** Authentication-enforced views; each user only sees their own data.
- **Diagnostics & Demo Scripts:** `create_sample_data.py`, `debug_frontend.py`, `demo_commands.sh`, and SQL examples at `docs/sql.md`.

## Architecture Overview

| Layer    | Description                                                  |
| -------- | ------------------------------------------------------------ |
| Frontend | Django Templates + Bootstrap 5 + Font Awesome; static files in `myapp/static`. |
| Backend  | Django 5.2.8 class-based views (`CosmeticProductListView`, `Create/Update/Delete`, `ExpiringProductsView`), custom paginator, messages framework. |
| Database | SQLite (`db.sqlite3`) with models Brand, Category, CosmeticProduct, UsageLog; indexed on `(expiration_date, status)` and `(brand, category)`. |
| Scripts  | `create_sample_data.py` (seed), `debug_frontend.py` (view introspection), `demo_commands.sh` (run pip + server). |

## Project Layout

```
5003_Projects-main/
├── manage.py                # Django entry point
├── myproject/               # Project configuration (settings, urls, wsgi)
├── myapp/                   # Business logic (models, views, urls, templates, static)
├── docs/                    # AGENTS.md, demo outline, scripts, SQL, report requirements
├── SDSC5003_Report/         # LaTeX sources and diagrams
├── create_sample_data.py    # Seed data script
├── debug_frontend.py        # Diagnostics for list view and template context
├── demo_commands.sh         # Interactive CLI helper (pip install + runserver)
└── requirements.txt         # Python dependencies
```

## Prerequisites

- Python 3.13 (Anaconda environment works).
- pip / virtualenv recommended.
- SQLite (bundled with Python).

## Installation & Setup

```bash
git clone https://github.com/nerissasnow/5003_Projects.git
cd 5003_Projects-main

# (Optional) create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Load sample data (creates test user `testuser` with sample cosmetics)
python create_sample_data.py
```

## Running the Application

### Option A: Manual commands

```bash
python manage.py runserver 127.0.0.1:8000
```

Access `http://127.0.0.1:8000/myapp/login/` and log in with seeded credentials (see seed script output). Use the navbar to navigate Product List, Add Product, and Expiring Soon pages.

### Option B: Interactive helper script

```bash
chmod +x demo_commands.sh
./demo_commands.sh
```

Press Enter when prompted to execute `pip install -r requirements.txt` and `python manage.py runserver`. The script writes the server PID to `.demo_runserver.pid`; stop it via `kill $(cat .demo_runserver.pid) && rm .demo_runserver.pid`.

## Diagnostics

- `debug_frontend.py`: inspects the list view QuerySet and context (useful when UI shows no rows).

## Testing Notes

- Django messages and login/logout flows are protected via `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` in `myproject/settings.py`.
- File uploads (product images) require configuring `MEDIA_ROOT`/`MEDIA_URL` before deployment.
- For production, switch `DEBUG=False`, configure allowed hosts, and migrate to PostgreSQL if high concurrency is expected.
