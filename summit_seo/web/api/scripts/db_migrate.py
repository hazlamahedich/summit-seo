#!/usr/bin/env python3
"""
Script for database migration management.
This script applies SQL migration files in order and tracks which migrations
have already been applied to avoid duplicate execution.
"""

import os
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("db_migrate")

# Load environment variables
load_dotenv()

# Migration directory
BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_connection():
    """
    Create a database connection.
    
    Returns:
        Connection: A database connection.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)
        
    try:
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)


def ensure_migration_table(conn):
    """
    Ensure the migration table exists.
    
    Args:
        conn (Connection): Database connection.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            logger.info("Migration table checked/created")
    except Exception as e:
        logger.error(f"Failed to create migration table: {e}")
        sys.exit(1)


def get_applied_migrations(conn):
    """
    Get list of already applied migrations.
    
    Args:
        conn (Connection): Database connection.
        
    Returns:
        list: List of applied migration filenames.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT migration_name FROM schema_migrations ORDER BY id")
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Failed to get applied migrations: {e}")
        sys.exit(1)


def get_migration_files():
    """
    Get list of migration files.
    
    Returns:
        list: List of migration files sorted by name.
    """
    try:
        migration_files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')]
        migration_files.sort()
        return migration_files
    except Exception as e:
        logger.error(f"Failed to get migration files: {e}")
        sys.exit(1)


def apply_migration(conn, migration_file):
    """
    Apply a migration file.
    
    Args:
        conn (Connection): Database connection.
        migration_file (str): Name of the migration file.
    """
    migration_path = MIGRATIONS_DIR / migration_file
    
    try:
        # Read migration file
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        # Start a transaction
        with conn.cursor() as cur:
            # Execute the migration
            cur.execute(sql)
            
            # Record the migration
            cur.execute(
                "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                (migration_file,)
            )
            
        logger.info(f"Applied migration: {migration_file}")
    except Exception as e:
        logger.error(f"Failed to apply migration {migration_file}: {e}")
        conn.rollback()
        sys.exit(1)


def create_migration(migration_name):
    """
    Create a new migration file.
    
    Args:
        migration_name (str): Name for the migration.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{migration_name}.sql"
    file_path = MIGRATIONS_DIR / filename
    
    try:
        with open(file_path, 'w') as f:
            f.write(f"-- Migration: {migration_name}\n")
            f.write(f"-- Created at: {datetime.now().isoformat()}\n\n")
            
        logger.info(f"Created migration file: {filename}")
    except Exception as e:
        logger.error(f"Failed to create migration file: {e}")
        sys.exit(1)


def main():
    """Main function to run migrations."""
    parser = argparse.ArgumentParser(description="Database migration manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Apply pending migrations")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("name", help="Name for the migration")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_migration(args.name)
    elif args.command == "migrate":
        conn = get_connection()
        ensure_migration_table(conn)
        
        applied_migrations = get_applied_migrations(conn)
        migration_files = get_migration_files()
        
        for migration_file in migration_files:
            if migration_file not in applied_migrations:
                logger.info(f"Applying migration: {migration_file}")
                apply_migration(conn, migration_file)
    elif args.command == "status":
        conn = get_connection()
        ensure_migration_table(conn)
        
        applied_migrations = set(get_applied_migrations(conn))
        migration_files = get_migration_files()
        
        logger.info("Migration status:")
        for migration_file in migration_files:
            status = "Applied" if migration_file in applied_migrations else "Pending"
            logger.info(f"  [{status}] {migration_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 