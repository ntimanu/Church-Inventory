#!/usr/bin/env python
"""
Church Inventory System: Full Database Validation Script
Checks:
1. psycopg2 raw connection
2. Django ORM connection
3. Model validation
4. Migration check
5. Object count in key models
"""
import os
import sys
import django
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_inventory_project.settings')

def test_psycopg2_connection():
    """Direct PostgreSQL connection using psycopg2"""
    try:
        from django.conf import settings
        db = settings.DATABASES['default']
        
        print(f"Connecting to PostgreSQL ({db['NAME']} @ {db['HOST']}:{db['PORT']})...")
        
        conn = psycopg2.connect(
            dbname=db['NAME'],
            user=db['USER'],
            password=db['PASSWORD'],
            host=db['HOST'],
            port=db['PORT']
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✅ psycopg2 connected! PostgreSQL version: {version}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ psycopg2 connection failed: {e}")
        return False

def test_django_connection():
    """Test Django ORM database connection"""
    try:
        django.setup()
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone()[0] == 1:
                print("✅ Django ORM connection successful!")
                return True
        return False
    except OperationalError as e:
        print(f"❌ Django connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Django ORM error: {e}")
        return False

def validate_models():
    """Run Django system checks on models"""
    from django.core.management import call_command
    from io import StringIO
    print("\nValidating models...")
    out = StringIO()
    try:
        call_command('check', stdout=out)
        res = out.getvalue()
        if "System check identified no issues" in res:
            print("✅ Models are valid!")
        else:
            print("❌ Issues found in models:")
            print(res)
    except Exception as e:
        print(f"❌ Model check failed: {e}")

def check_migrations():
    """Check for unapplied migrations"""
    from django.core.management import call_command
    from io import StringIO
    print("\nChecking migrations...")
    out = StringIO()
    try:
        call_command('showmigrations', stdout=out)
        result = out.getvalue()
        print("Migration status:\n" + result)
        if "[ ]" in result:
            print("⚠️ Some migrations are not applied. Run `python manage.py migrate`.")
        else:
            print("✅ All migrations are applied.")
    except Exception as e:
        print(f"❌ Migration check failed: {e}")

def count_model_objects():
    """Count records in core models"""
    print("\nCounting model objects...")
    try:
        from users.models import User
        from ministry_areas.models import MinistryArea
        from inventory.models import Category, Item, InventoryTransaction, Maintenance, ItemCheckout
        models = [
            (User, "Users"),
            (MinistryArea, "Ministry Areas"),
            (Category, "Categories"),
            (Item, "Items"),
            (InventoryTransaction, "Transactions"),
            (Maintenance, "Maintenance Records"),
            (ItemCheckout, "Item Checkouts"),
        ]
        for model, label in models:
            try:
                count = model.objects.count()
                print(f"✅ {label}: {count}")
            except Exception as e:
                print(f"❌ {label} error: {e}")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")

def main():
    print("\n" + "="*60)
    print("🔍 CHURCH INVENTORY SYSTEM - DATABASE VALIDATION")
    print("="*60)
    
    psycopg2_ok = test_psycopg2_connection()
    orm_ok = test_django_connection()

    if psycopg2_ok and orm_ok:
        validate_models()
        check_migrations()
        count_model_objects()
    else:
        print("\n⚠️ Skipping deeper checks due to DB connection failure.")

    print("\n" + "="*60)

if __name__ == "__main__":
    sys.exit(main())
