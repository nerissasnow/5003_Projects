Cosmetic Management System


A Django-based cosmetic inventory management system that helps users effectively manage personal cosmetics, track product expiration dates, and avoid waste.

Features

• Full Product Lifecycle Management - Add, edit, delete cosmetic products

• Smart Expiration Alerts - 4-level warning system (Good/Soon/Urgent/Expired)

• Multi-dimensional Classification - Organize by brand, category, status

• Data Analytics - Inventory statistics and expiration trends

• Multi-user Support - User data isolation and security

• Responsive Design - Desktop and mobile support

• Single-File Distribution - Packaged as standalone executable

Quick Start

Prerequisites

• Python 3.8+

• Django 4.2+

• SQLite/PostgreSQL

Installation Steps

1. Clone Repository
git clone https://github.com/yourusername/cosmetic-management-system.git
cd cosmetic-management-system


2. Install Dependencies
pip install -r requirements.txt


3. Database Migration
python manage.py migrate


4. Create Superuser
python manage.py createsuperuser


5. Start Development Server
python manage.py runserver


6. Access System
Open browser and visit: http://127.0.0.1:8000

Default Account

• Username: liyifei

• Password: 123456

Project Structure


cosmetic-management-system/

├── cosmetic_manager/     # Django project configuration

├── myapp/               # Main application

│   ├── models.py        # Data models

│   ├── views.py         # View logic

│   ├── urls.py          # URL routing

│   └── templates/       # Frontend templates

├── static/              # Static assets

└── manage.py           # Management script


Data Models

The system includes these core data models:

• User - System user management

• Brand - Cosmetic brand information

• Category - Product categorization system

• CosmeticProduct - Core product data

• UsageLog - Product usage history

Database Design Features

• Third Normal Form - Minimal data redundancy

• Composite Index Optimization - Query performance optimization

• Data Integrity Constraints - Business rule enforcement

• Clear Foreign Key Relationships - Proper data associations

Development Guide

Environment Setup

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install development dependencies
pip install -r requirements.txt


Running Tests

python manage.py test myapp


Code Style

# Code formatting
black .
flake8 .


Packaging & Distribution

Single-File Packaging (Recommended)

# Package with PyInstaller
pyinstaller --onefile run.py

# Packaged files located in dist/ directory


Multi-Platform Support

• Windows: .exe executable

• macOS: Unix executable

• Linux: Universal executable

🔧 Configuration

Database Configuration

Uses SQLite by default, PostgreSQL recommended for production:
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cosmetic_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


Static Files Configuration

# Development
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Production
STATIC_ROOT = BASE_DIR / 'staticfiles'


API Endpoints

RESTful API endpoints available:

Endpoint Method Description

/api/products/ GET, POST Product list/create

/api/products/{id}/ GET, PUT, DELETE Product detail/update/delete

/api/categories/ GET Category list

/api/expiring/ GET Expiring products

Troubleshooting

Common Issues

Q: Static files not loading
python manage.py collectstatic


Q: Database migration fails
python manage.py makemigrations
python manage.py migrate


Q: Port already in use
python manage.py runserver 8001
