#!/usr/bin/env python
"""
Script to create the initial database migration.
Run this script after setting up the database models to create the initial migration.

Example:
    python migrations/create_initial_migration.py
"""
import os
import sys
import alembic.config
from pathlib import Path

# Add the parent directory to sys.path to be able to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """
    Create the initial database migration.
    """
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Change to the directory containing alembic.ini
    os.chdir(script_dir)
    
    # Create the alembic configuration
    alembic_args = [
        '--raiseerr',
        'revision',
        '--autogenerate',
        '-m', 'Initial database creation'
    ]
    
    # Run the alembic command
    alembic.config.main(argv=alembic_args)
    
    print("Initial migration created successfully!")

if __name__ == "__main__":
    main() 