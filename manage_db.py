#!/usr/bin/env python
"""
Database management utility script for Church Inventory System.

This script provides convenient commands for common database operations.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project directory to the path so we can import Django settings
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_inventory_project.settings')

def run_command(command):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def create_superuser():
    """Create a Django superuser interactively"""
    try:
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if User.objects.filter(is_superuser=True).exists():
            print("Superuser already exists. Creating a new one...")
        
        username = input("Enter username: ")
        email = input("Enter email: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        password = input("Enter password: ")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        print(f"Superuser {username} created successfully!")
        return True
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return False

def reset_db():
    """Reset the database by dropping and recreating it"""
    from django.conf import settings
    
    # Extract database connection info from settings
    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings['HOST']
    db_port = db_settings['PORT']
    
    # PostgreSQL commands
    drop_cmd = f'PGPASSWORD="{db_password}" dropdb -h {db_host} -p {db_port} -U {db_user} {db_name}'
    create_cmd = f'PGPASSWORD="{db_password}" createdb -h {db_host} -p {db_port} -U {db_user} {db_name}'
    
    print(f"Dropping database '{db_name}'...")
    if run_command(drop_cmd):
        print(f"Creating database '{db_name}'...")
        if run_command(create_cmd):
            print("Database reset successful.")
            return True
    
    print("Database reset failed.")
    return False

def main():
    """Main function for parsing arguments and executing commands"""
    parser = argparse.ArgumentParser(description='Database management utility for Church Inventory System')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run Django migrations')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset the database')
    
    # Createsuperuser command
    superuser_parser = subparsers.add_parser('createsuperuser', help='Create a Django superuser')
    
    # Setup command (for initial setup)
    setup_parser = subparsers.add_parser('setup', help='Run complete initial setup')
    
    # Test DB connection command
    test_parser = subparsers.add_parser('test_connection', help='Test database connection')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'migrate':
        run_command('python manage.py migrate')
    elif args.command == 'reset':
        if reset_db():
            run_command('python manage.py migrate')
    elif args.command == 'createsuperuser':
        create_superuser()
    elif args.command == 'setup':
        if run_command('python manage.py migrate'):
            create_superuser()
    elif args.command == 'test_connection':
        # Test database connection using Django settings
        try:
            import django
            django.setup()
            from django.db import connections
            from django.db.utils import OperationalError
            
            conn = connections['default']
            try:
                conn.cursor()
                print("Database connection successful!")
            except OperationalError:
                print("Database connection failed!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()