# Church Inventory Management System - Setup Guide

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- virtualenv or venv (recommended)
- Git (optional but recommended)

## PostgreSQL Setup

### 1. Install PostgreSQL

#### On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### On macOS (using Homebrew):

```bash
brew install postgresql
```

#### On Windows:

Download and install from the [official PostgreSQL website](https://www.postgresql.org/download/windows/).

### 2. Create a Database

First, log in to PostgreSQL as the postgres user:

```bash
# On Linux
sudo -u postgres psql

# On macOS
psql postgres

# On Windows (in command prompt after adding PostgreSQL bin directory to PATH)
psql -U postgres
```

Once logged in, create a database and user:

```sql
CREATE DATABASE church_inventory;
CREATE USER church_user WITH PASSWORD 'your_secure_password';
ALTER ROLE church_user SET client_encoding TO 'utf8';
ALTER ROLE church_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE church_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE church_inventory TO church_user;
\q
```

## Project Setup

### 1. Clone the Repository (or create a new project directory)

```bash
git clone https://github.com/yourusername/church-inventory.git
cd church-inventory
```

Or create a new directory if not using git:

```bash
mkdir church-inventory
cd church-inventory
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv church_env

# Activate the virtual environment
# On Windows:
church_env\Scripts\activate

# On macOS/Linux:
source church_env/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

If you're starting from scratch, install these packages:

```bash
pip install django==4.2.11 djangorestframework djangorestframework-simplejwt psycopg2-binary python-dotenv django-cors-headers pillow
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following contents:

```
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=church_inventory
DB_USER=church_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

Be sure to replace `your_secret_key_here` with a secure random string and `your_secure_password` with the password you set earlier.

### 5. Run Migrations

```bash
python manage.py makemigrations users
python manage.py makemigrations ministry_areas
python manage.py makemigrations inventory
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 7. Load Initial Data (Optional)

If you want to populate the database with sample data:

```bash
python manage.py loaddata ministry_areas/fixtures/initial_data.json
python manage.py loaddata inventory/fixtures/categories.json
python manage.py loaddata inventory/fixtures/items.json
```

### 8. Run
