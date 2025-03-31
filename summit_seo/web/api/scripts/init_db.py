#!/usr/bin/env python
"""
Database initialization script for Summit SEO.
This script creates the initial database and applies migrations.

Example:
    python scripts/init_db.py
"""
import os
import sys
import argparse
import alembic.config
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy_utils import database_exists, create_database
from summit_seo.web.api.models.database import engine

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Initialize the Summit SEO database")
    parser.add_argument("--recreate", action="store_true", 
                        help="Recreate the database if it exists")
    return parser.parse_args()

def run_migrations():
    """Run database migrations using Alembic."""
    # Get the directory of migrations folder
    migrations_dir = Path(__file__).parent.parent.joinpath("migrations").absolute()
    
    # Change to the directory containing alembic.ini
    os.chdir(migrations_dir)
    
    # Run the migrations
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head'
    ]
    
    # Run the alembic command
    alembic.config.main(argv=alembic_args)

def seed_data():
    """Seed the database with initial data."""
    # Import models here to avoid circular imports
    from summit_seo.web.api.models import Role, User
    from summit_seo.web.api.models.database import SessionLocal
    from passlib.context import CryptContext
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create default roles if they don't exist
        roles = {
            "admin": "System administrator with full access",
            "manager": "Tenant manager with administrative access to tenant resources",
            "user": "Regular user with basic access"
        }
        
        for role_name, description in roles.items():
            if not db.query(Role).filter(Role.name == role_name).first():
                role = Role(name=role_name, description=description)
                db.add(role)
        
        db.commit()
        
        # Create admin user if it doesn't exist
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@summit-seo.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")  # Default password for development
        
        # Hash the password
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(admin_password)
        
        if not db.query(User).filter(User.email == admin_email).first():
            # Get admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            
            # Create admin user
            admin_user = User(
                email=admin_email,
                username="admin",
                password_hash=hashed_password,
                is_active=True,
                is_verified=True,
                first_name="Admin",
                last_name="User"
            )
            
            admin_user.roles.append(admin_role)
            db.add(admin_user)
            db.commit()
            
            print(f"Created admin user: {admin_email}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

def main():
    """Initialize the database."""
    args = parse_args()
    
    # Get the database URL from the engine
    db_url = str(engine.url)
    
    # Check if the database exists
    if not database_exists(db_url):
        print(f"Creating database: {db_url}")
        create_database(db_url)
    elif args.recreate:
        if input("This will delete all existing data. Are you sure? (y/n): ").lower() == 'y':
            from sqlalchemy_utils import drop_database
            print(f"Dropping database: {db_url}")
            drop_database(db_url)
            print(f"Creating database: {db_url}")
            create_database(db_url)
        else:
            print("Database recreation cancelled.")
            return
    
    # Run migrations
    print("Running database migrations...")
    run_migrations()
    
    # Seed initial data
    print("Seeding initial data...")
    seed_data()
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main() 