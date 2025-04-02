#!/usr/bin/env python3
"""
Schema validation script to ensure SQL schema and Python models are in sync.
This script compares the defined SQLAlchemy models with the database schema
to identify inconsistencies in column names, types, and relationships.
"""

import os
import sys
import logging
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

import sqlalchemy as sa
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.engine import reflection
from sqlalchemy import create_engine, inspect as sa_inspect
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("schema_validator")

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"


def get_engine():
    """Create a SQLAlchemy engine from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)
        
    try:
        return create_engine(db_url)
    except Exception as e:
        logger.error(f"Failed to create engine: {e}")
        sys.exit(1)


def get_all_models() -> Dict[str, DeclarativeMeta]:
    """
    Dynamically import and collect all SQLAlchemy models.
    
    Returns:
        Dict[str, DeclarativeMeta]: Dictionary of table name to model class
    """
    models = {}
    
    # Get all python files in the models directory
    model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.py') and f != '__init__.py']
    
    for model_file in model_files:
        module_name = model_file[:-3]  # Remove .py extension
        try:
            # Import the module
            module = importlib.import_module(f"models.{module_name}")
            
            # Find all classes that are SQLAlchemy models
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, '__tablename__') and hasattr(obj, '__table__'):
                    # Skip abstract models
                    if hasattr(obj, '__abstract__') and obj.__abstract__:
                        continue
                    
                    # Add to our models dictionary
                    models[obj.__tablename__] = obj
        except Exception as e:
            logger.warning(f"Failed to import models from {module_name}: {e}")
    
    return models


def get_db_tables(engine) -> Dict[str, Dict]:
    """
    Get all tables and their columns from the database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        Dict[str, Dict]: Dictionary of table name to table info
    """
    inspector = reflection.Inspector.from_engine(engine)
    tables = {}
    
    for table_name in inspector.get_table_names():
        tables[table_name] = {
            'columns': {col['name']: col for col in inspector.get_columns(table_name)},
            'foreign_keys': inspector.get_foreign_keys(table_name),
            'indexes': inspector.get_indexes(table_name),
            'primary_keys': inspector.get_pk_constraint(table_name)['constrained_columns']
        }
    
    return tables


def get_model_columns(model) -> Dict[str, Dict]:
    """
    Get all columns from a SQLAlchemy model.
    
    Args:
        model: SQLAlchemy model class
        
    Returns:
        Dict[str, Dict]: Dictionary of column name to column info
    """
    inspector = sa_inspect(model)
    columns = {}
    
    for column in inspector.columns:
        col_info = {
            'name': column.name,
            'type': column.type,
            'nullable': column.nullable,
            'default': column.default,
            'primary_key': column.primary_key,
            'foreign_keys': [fk.target_fullname for fk in column.foreign_keys]
        }
        columns[column.name] = col_info
    
    return columns


def get_model_relationships(model) -> List[Dict]:
    """
    Get all relationships from a SQLAlchemy model.
    
    Args:
        model: SQLAlchemy model class
        
    Returns:
        List[Dict]: List of relationship info dictionaries
    """
    inspector = sa_inspect(model)
    relationships = []
    
    for relationship in inspector.relationships:
        rel_info = {
            'name': relationship.key,
            'target': relationship.target.name,
            'direction': relationship.direction.name
        }
        relationships.append(rel_info)
    
    return relationships


def validate_model_columns(model, db_table) -> List[str]:
    """
    Validate that all columns in a model exist in the database.
    
    Args:
        model: SQLAlchemy model class
        db_table: Database table info
        
    Returns:
        List[str]: List of inconsistencies found
    """
    inconsistencies = []
    model_columns = get_model_columns(model)
    
    # Check for columns in model but not in DB
    for col_name, col_info in model_columns.items():
        if col_name not in db_table['columns']:
            inconsistencies.append(f"Column '{col_name}' exists in model but not in database table")
            continue
            
        # Check column types - this is complex due to dialect differences
        # Basic check for major type differences
        db_col = db_table['columns'][col_name]
        model_type = str(col_info['type'])
        db_type = str(db_col['type'])
        
        # Very basic type compatibility check - would need more sophistication in a real implementation
        if ('INT' in db_type.upper() and 'INT' not in model_type.upper()) or \
           ('VARCHAR' in db_type.upper() and 'VARCHAR' not in model_type.upper() and 'String' not in model_type) or \
           ('BOOLEAN' in db_type.upper() and 'BOOLEAN' not in model_type.upper() and 'Boolean' not in model_type) or \
           ('UUID' in db_type.upper() and 'UUID' not in model_type.upper()):
            inconsistencies.append(f"Column '{col_name}' has different types: Model={model_type}, DB={db_type}")
    
    # Check for columns in DB but not in model (exclude standard columns)
    standard_columns = {'id', 'created_at', 'updated_at', 'is_deleted', 'tenant_id'}
    for col_name in db_table['columns']:
        if col_name not in model_columns and col_name not in standard_columns:
            inconsistencies.append(f"Column '{col_name}' exists in database but not in model")
    
    return inconsistencies


def validate_model_relationships(model, db_tables) -> List[str]:
    """
    Validate relationships defined in a model against the database.
    
    Args:
        model: SQLAlchemy model class
        db_tables: Dictionary of all database tables
        
    Returns:
        List[str]: List of inconsistencies found
    """
    inconsistencies = []
    model_rels = get_model_relationships(model)
    
    # Get all foreign keys in the database for this table
    db_foreign_keys = []
    if model.__tablename__ in db_tables:
        for fk in db_tables[model.__tablename__]['foreign_keys']:
            db_foreign_keys.append({
                'constrained_columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            })
    
    # For each relationship in the model, check if there's a corresponding FK in the DB
    # This is a simplified check and might miss some cases
    for rel in model_rels:
        target_table = rel['target']
        found_fk = False
        
        for fk in db_foreign_keys:
            if fk['referred_table'] == target_table:
                found_fk = True
                break
                
        if not found_fk and rel['direction'] == 'MANYTOONE':
            # Many-to-one relationships should have a corresponding FK
            inconsistencies.append(f"Relationship '{rel['name']}' to '{target_table}' has no corresponding foreign key in the database")
    
    return inconsistencies


def main():
    """Main function to validate schema."""
    try:
        engine = get_engine()
        db_tables = get_db_tables(engine)
        models = get_all_models()
        
        total_inconsistencies = 0
        
        # Validate each model
        for table_name, model in models.items():
            logger.info(f"Validating model: {model.__name__}")
            inconsistencies = []
            
            # Check if table exists in DB
            if table_name not in db_tables:
                logger.error(f"Table '{table_name}' defined in model does not exist in database")
                total_inconsistencies += 1
                continue
                
            # Validate columns
            col_inconsistencies = validate_model_columns(model, db_tables[table_name])
            inconsistencies.extend(col_inconsistencies)
            
            # Validate relationships
            rel_inconsistencies = validate_model_relationships(model, db_tables)
            inconsistencies.extend(rel_inconsistencies)
            
            # Report inconsistencies for this model
            if inconsistencies:
                logger.warning(f"Found {len(inconsistencies)} inconsistencies in {model.__name__}:")
                for i, issue in enumerate(inconsistencies, 1):
                    logger.warning(f"  {i}. {issue}")
                total_inconsistencies += len(inconsistencies)
            else:
                logger.info(f"✓ Model {model.__name__} is consistent with database schema")
        
        # Check for tables in DB but not in models
        for table_name in db_tables:
            if table_name not in models and not table_name.startswith('schema_migrations'):
                logger.warning(f"Table '{table_name}' exists in database but has no corresponding model")
                total_inconsistencies += 1
        
        # Final report
        if total_inconsistencies == 0:
            logger.info("✓ All models are consistent with database schema")
            return 0
        else:
            logger.warning(f"Found {total_inconsistencies} inconsistencies between models and database schema")
            return 1
            
    except Exception as e:
        logger.error(f"Error validating schema: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 