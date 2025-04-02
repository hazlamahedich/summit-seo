#!/usr/bin/env python3
"""
Model update script to automatically update Python model definitions
based on the database schema. This helps ensure consistency between 
the SQLAlchemy models and the actual database structure.
"""

import os
import sys
import re
import logging
from pathlib import Path
import importlib
import inspect
import tempfile
import shutil
from enum import Enum

import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.engine import reflection
from sqlalchemy.ext.declarative import DeclarativeMeta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("model_updater")

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


def get_all_models() -> dict:
    """
    Dynamically import and collect all SQLAlchemy models.
    
    Returns:
        dict: Dictionary of table name to model class
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
                    models[obj.__tablename__] = {
                        'class': obj,
                        'module': module,
                        'file': model_file
                    }
        except Exception as e:
            logger.warning(f"Failed to import models from {module_name}: {e}")
    
    return models


def get_db_tables(engine) -> dict:
    """
    Get all tables and their columns from the database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        dict: Dictionary of table name to table info
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


def get_db_enums(engine) -> dict:
    """
    Get all enum types from the database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        dict: Dictionary of enum name to enum values
    """
    enums = {}
    
    try:
        with engine.connect() as conn:
            # Query to get all enum types and their values
            result = conn.execute(text("""
                SELECT 
                    t.typname AS enum_name,
                    array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
                FROM 
                    pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                GROUP BY 
                    t.typname
                ORDER BY 
                    t.typname;
            """))
            
            for row in result:
                enum_name = row[0]
                enum_values = row[1]
                enums[enum_name] = enum_values
    except Exception as e:
        logger.error(f"Failed to get enum types: {e}")
    
    return enums


def generate_enum_class(enum_name, enum_values):
    """
    Generate Python enum class definition from database enum type.
    
    Args:
        enum_name (str): Name of the enum
        enum_values (list): List of enum values
        
    Returns:
        str: Python code for the enum class
    """
    # Convert to camel case for class name
    class_name = ''.join(word.capitalize() for word in enum_name.split('_'))
    
    code = f"class {class_name}(enum.Enum):\n"
    code += f'    """Database enum for {enum_name}."""\n\n'
    
    # Add enum values
    for value in enum_values:
        # Convert to uppercase for enum constants
        constant_name = value.upper()
        code += f'    {constant_name} = "{value}"\n'
    
    code += "\n\n"
    return code


def update_model_file(file_path, db_tables, db_enums):
    """
    Update a model file to match the database schema.
    
    Args:
        file_path (Path): Path to the model file
        db_tables (dict): Database tables info
        db_enums (dict): Database enum types
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    if not file_path.exists():
        logger.error(f"File {file_path} does not exist")
        return False
    
    # Read the original file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    updated_content = content
    
    # Check for enums that need to be added or updated
    for enum_name, enum_values in db_enums.items():
        # Convert to camel case for class name
        class_name = ''.join(word.capitalize() for word in enum_name.split('_'))
        
        # Check if enum class already exists
        if re.search(rf'class\s+{class_name}\s*\(\s*enum\.Enum\s*\)', content):
            # Enum class exists, check if values need to be updated
            enum_pattern = rf'class\s+{class_name}\s*\(\s*enum\.Enum\s*\)[^{{}}]+?(?=\n\n|\Z)'
            enum_match = re.search(enum_pattern, content, re.DOTALL)
            
            if enum_match:
                enum_def = enum_match.group()
                
                # Check if all values are present
                missing_values = []
                for value in enum_values:
                    if f'"{value}"' not in enum_def and f"'{value}'" not in enum_def:
                        missing_values.append(value)
                
                if missing_values:
                    logger.info(f"Enum {class_name} is missing values: {missing_values}")
                    
                    # Add missing values
                    new_enum_def = enum_def
                    for value in missing_values:
                        constant_name = value.upper()
                        new_enum_def += f'    {constant_name} = "{value}"\n'
                    
                    # Replace old enum definition with new one
                    updated_content = updated_content.replace(enum_def, new_enum_def)
        else:
            # Enum class doesn't exist, add it
            logger.info(f"Adding new enum class {class_name}")
            
            # Generate enum class code
            enum_code = generate_enum_class(enum_name, enum_values)
            
            # Add import if needed
            if "import enum" not in content and "from enum import" not in content:
                updated_content = "import enum\n" + updated_content
            
            # Add enum class after imports
            imports_end = max(
                updated_content.rfind("import", 0, 500),
                updated_content.rfind("from", 0, 500)
            )
            
            if imports_end > 0:
                imports_end = updated_content.find("\n", imports_end) + 1
                updated_content = updated_content[:imports_end] + "\n" + enum_code + updated_content[imports_end:]
            else:
                # Add at the beginning if no imports found
                updated_content = enum_code + updated_content
    
    # Check if content was updated
    if updated_content != content:
        # Create a backup of the original file
        backup_path = file_path.with_suffix('.py.bak')
        shutil.copy2(file_path, backup_path)
        
        # Write the updated content
        with open(file_path, 'w') as f:
            f.write(updated_content)
            
        logger.info(f"Updated model file {file_path}")
        return True
    
    return False


def update_model_column_types(file_path, model_info, db_tables, db_enums):
    """
    Update column types in a model file to match the database schema.
    
    Args:
        file_path (Path): Path to the model file
        model_info (dict): Model class info
        db_tables (dict): Database tables info
        db_enums (dict): Database enum types
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    if not file_path.exists():
        logger.error(f"File {file_path} does not exist")
        return False
    
    model_class = model_info['class']
    table_name = model_class.__tablename__
    
    if table_name not in db_tables:
        logger.warning(f"Table {table_name} not found in database")
        return False
    
    db_table = db_tables[table_name]
    
    # Read the original file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    updated_content = content
    
    # Find column definitions in the model
    for col_name, db_col in db_table['columns'].items():
        # Skip standard columns that are likely defined in a base class
        if col_name in {'id', 'created_at', 'updated_at', 'is_deleted', 'tenant_id'}:
            continue
        
        # Look for column definition in the file
        col_pattern = rf'(\s+){col_name}\s*=\s*Column\s*\('
        col_match = re.search(col_pattern, content)
        
        if col_match:
            # Found column definition, check if type matches
            indent = col_match.group(1)
            start_pos = col_match.start()
            
            # Find the end of the column definition
            paren_count = 0
            end_pos = start_pos
            for i in range(start_pos, len(content)):
                if content[i] == '(':
                    paren_count += 1
                elif content[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > start_pos:
                col_def = content[start_pos:end_pos]
                
                # Check for enum columns
                db_type = db_col['type']
                if hasattr(db_type, 'name') and db_type.name in db_enums:
                    enum_name = db_type.name
                    class_name = ''.join(word.capitalize() for word in enum_name.split('_'))
                    
                    # Check if the column is using Enum type
                    if f"Enum({class_name})" not in col_def:
                        logger.info(f"Column {col_name} should use Enum({class_name})")
                        
                        # Replace column type with Enum
                        new_col_def = re.sub(
                            r'Column\s*\(\s*([^,]+)',
                            f'Column(Enum({class_name})',
                            col_def
                        )
                        
                        # Replace old column definition with new one
                        updated_content = updated_content.replace(col_def, new_col_def)
    
    # Check if content was updated
    if updated_content != content:
        # Create a backup of the original file
        backup_path = file_path.with_suffix('.py.bak')
        shutil.copy2(file_path, backup_path)
        
        # Write the updated content
        with open(file_path, 'w') as f:
            f.write(updated_content)
            
        logger.info(f"Updated column types in {file_path}")
        return True
    
    return False


def main():
    """Main function to update models."""
    try:
        engine = get_engine()
        db_tables = get_db_tables(engine)
        db_enums = get_db_enums(engine)
        models = get_all_models()
        
        updated_files = 0
        
        # Update each model file
        for table_name, model_info in models.items():
            file_path = MODELS_DIR / model_info['file']
            
            # First update enums
            if update_model_file(file_path, db_tables, db_enums):
                updated_files += 1
            
            # Then update column types
            if update_model_column_types(file_path, model_info, db_tables, db_enums):
                updated_files += 1
        
        if updated_files > 0:
            logger.info(f"Updated {updated_files} model files to match database schema")
        else:
            logger.info("All model files are already up to date")
        
        return 0
    except Exception as e:
        logger.error(f"Error updating models: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 