# Database Schema and Migrations

This directory contains the SQL migration files for the Summit SEO application's database schema. These migrations define the structure of the database and ensure consistency across environments.

## Migration Files

- `01_initial_schema.sql`: Creates all tables, indexes, and enum types
- `02_row_level_security.sql`: Implements Row Level Security (RLS) policies

## Schema Overview

The database schema follows a multi-tenant design with the following core tables:

1. **Authentication tables**: `user`, `role`, `user_roles`
2. **Multi-tenant tables**: `tenant`, `tenant_user`
3. **SEO Analysis tables**: `project`, `analysis`, `finding`, `recommendation`

See the full schema documentation in `../docs/database_schema.md`.

## Migration Process

Use the `db_migrate.py` script in the `../scripts` directory to apply migrations:

```bash
# Apply all pending migrations
python scripts/db_migrate.py migrate

# Show migration status
python scripts/db_migrate.py status

# Create a new migration
python scripts/db_migrate.py create migration_name
```

The script tracks applied migrations in a `schema_migrations` table to avoid duplicate execution.

## Schema Validation

### Ensuring Consistency

To ensure that the SQL schema and Python models remain consistent, use the provided validation tools:

1. **validate_schema.py**: Checks that SQLAlchemy models match the database schema
   ```bash
   python scripts/validate_schema.py
   ```

2. **update_models.py**: Updates Python models to match the database schema
   ```bash
   python scripts/update_models.py
   ```

### Key Points of Consistency

- **Enum Types**: In the SQL schema, enums are defined as PostgreSQL enum types. In Python models, they are defined as Python Enum classes.
- **Column Types**: Column types need to be consistent between Python models and SQL schema.
- **Relationships**: Foreign keys in the database should match relationships in the SQLAlchemy models.

## Row Level Security (RLS)

The schema implements comprehensive Row Level Security (RLS) policies to ensure data isolation in a multi-tenant environment:

- Users can only access their own data
- Tenant members can only access data from their tenants
- Admin users have access to all data
- Custom security functions validate permissions

## Schema Versioning

Database migrations follow a sequential approach:

1. Each migration is numbered for ordering
2. Migrations are tracked in the `schema_migrations` table
3. Once applied, migrations should not be modified

If schema changes are needed, create a new migration rather than modifying existing ones.

## Working with Supabase

When using Supabase:

1. Apply migrations through the Supabase SQL Editor
2. Ensure RLS policies are properly applied
3. Test access with different user roles
4. Use the Service Role key for admin access to tables with RLS 