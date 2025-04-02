# Summit SEO Database Schema

This document provides an overview of the Summit SEO database schema, detailing the tables, their relationships, and the purpose of each component.

## Core Tables

### User Authentication and Management

#### `user`
- Primary user account information
- Contains authentication data and personal information
- Fields:
  - `id`: UUID primary key
  - `email`: User's email address (unique)
  - `username`: User's username (unique)
  - `first_name`: User's first name
  - `last_name`: User's last name
  - `password_hash`: Hashed password
  - `is_active`: Whether the user account is active
  - `is_verified`: Whether the user's email is verified
  - `profile_picture_url`: URL to profile picture
  - Standard timestamps and deletion flag

#### `role`
- Defines user roles for authorization
- Fields:
  - `id`: UUID primary key
  - `name`: Role name (unique)
  - `description`: Role description
  - Standard timestamps and deletion flag

#### `user_roles`
- Junction table for many-to-many relationship between users and roles
- Fields:
  - `user_id`: Foreign key to user
  - `role_id`: Foreign key to role
  - Composite primary key of both fields

### Multi-tenant Support

#### `tenant`
- Organization or account that groups users and projects
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: UUID identifying the tenant organization
  - `name`: Tenant name
  - `domain`: Custom domain (optional)
  - `subdomain`: Custom subdomain (optional)
  - `owner_id`: Foreign key to user who owns the tenant
  - `logo_url`: Tenant logo URL
  - `primary_color`: Primary brand color
  - `secondary_color`: Secondary brand color
  - Standard timestamps and deletion flag

#### `tenant_user`
- Association between users and tenants with specific roles
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: Tenant UUID
  - `user_id`: User UUID
  - `role`: Role within the tenant (owner, admin, member)
  - `can_create_projects`: Permission to create projects
  - `can_delete_projects`: Permission to delete projects
  - `can_manage_users`: Permission to manage tenant users
  - Standard timestamps and deletion flag

### SEO Analysis

#### `project`
- Website or domain being analyzed
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: Tenant UUID
  - `name`: Project name
  - `description`: Project description
  - `url`: Website URL
  - `settings`: JSON configuration settings
  - `tags`: JSON array of tags for organization
  - `icon_url`: Project icon URL
  - `last_score`: Most recent analysis score
  - `score_change`: Change from previous analysis
  - `issues_count`: Total number of issues found
  - `critical_issues_count`: Number of critical issues
  - Standard timestamps and deletion flag

#### `analysis`
- Individual SEO analysis run
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: Tenant UUID
  - `status`: Analysis status (pending, running, completed, failed, cancelled)
  - `project_id`: Foreign key to project
  - `config`: JSON configuration used for this analysis
  - `score`: Overall SEO score (0-100)
  - `results`: JSON results by category
  - `started_at`: Unix timestamp when analysis started
  - `completed_at`: Unix timestamp when analysis completed
  - `duration`: Analysis duration in seconds
  - `error`: Error message if analysis failed
  - `error_details`: Detailed error information
  - `analyzer_versions`: JSON with analyzer versions used
  - `issues_count`: Total number of issues found
  - `critical_issues_count`: Number of critical issues
  - `high_issues_count`: Number of high issues
  - `medium_issues_count`: Number of medium issues
  - `low_issues_count`: Number of low issues
  - Standard timestamps and deletion flag

#### `finding`
- Individual issue or finding from an analysis
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: Tenant UUID
  - `analysis_id`: Foreign key to analysis
  - `analyzer`: Name of the analyzer that found this issue
  - `category`: Category of the finding
  - `rule_id`: Unique identifier for the rule that was checked
  - `title`: Finding title
  - `description`: Detailed description
  - `severity`: Severity level (critical, high, medium, low, info)
  - `locations`: JSON with locations in the site/code
  - `metadata`: Additional data specific to the finding
  - Standard timestamps and deletion flag

#### `recommendation`
- Actionable recommendation to improve SEO
- Fields:
  - `id`: UUID primary key
  - `tenant_id`: Tenant UUID
  - `analysis_id`: Foreign key to analysis
  - `finding_id`: Optional foreign key to finding
  - `title`: Recommendation title
  - `description`: Detailed description
  - `difficulty`: Implementation difficulty (1-10)
  - `impact`: Expected impact (1-10)
  - `priority`: Priority level (critical, high, medium, low)
  - `type`: Recommendation type (best_practice, quick_win, technical, etc.)
  - `implementation`: Implementation instructions
  - `code_examples`: JSON with code examples
  - `resources`: JSON with resources and references
  - `estimated_time`: Estimated implementation time in minutes
  - Standard timestamps and deletion flag

## Entity Relationship Diagram

```
                       +----------------+
                       |      User      |
                       +----------------+
                       | id             |
                       | email          |
                       | username       |
                       | password_hash  |
                       +-------+--------+
                               |
                +--------------|-------------+
                |              |             |
+---------------v-+    +-------v--------+   |
|     Role        |    |     Tenant     |   |
+----------------+|    +----------------+   |
| id             ||    | id             |<--+
| name           ||    | tenant_id      |
| description    ||    | name           |
+---------------+|+    | owner_id       |
                ||     +-------+--------+
                ||             |
                ||     +-------v--------+
                ||     | Tenant User    |
                ||     +----------------+
                ||     | id             |
                ||     | tenant_id      |
                ||     | user_id        |
                ||     | role           |
                ||     +----------------+
                ||
                ||             +----------------+
                ++------------>|    Project     |
                               +----------------+
                               | id             |
                               | tenant_id      |
                               | name           |
                               | url            |
                               +-------+--------+
                                       |
                                       |
                               +-------v--------+
                               |    Analysis    |
                               +----------------+
                               | id             |
                               | tenant_id      |
                               | project_id     |
                               | status         |
                               | score          |
                               +-------+--------+
                                       |
                  +--------------------+---------------------+
                  |                                          |
          +-------v--------+                      +----------v-------+
          |     Finding    |                      | Recommendation   |
          +----------------+                      +------------------+
          | id             |                      | id               |
          | tenant_id      |                      | tenant_id        |
          | analysis_id    |                      | analysis_id      |
          | analyzer       |                      | finding_id       |
          | severity       +--------------------->| priority         |
          +----------------+                      | difficulty       |
                                                  | impact           |
                                                  +------------------+
```

## Indexes

The following indexes are created for performance optimization:

- `user`: email, username, is_deleted
- `role`: name
- `tenant`: owner_id, is_deleted, tenant_id
- `project`: tenant_id, is_deleted
- `analysis`: project_id, tenant_id, status, is_deleted
- `finding`: analysis_id, tenant_id, severity, is_deleted
- `recommendation`: analysis_id, finding_id, tenant_id, is_deleted, priority, type

## Row Level Security

Row Level Security (RLS) policies are implemented to ensure:

1. Users can only access their own data or data they have permission to access
2. Admin users have access to all data
3. Tenant members can only access data from their tenants
4. Project data is restricted based on tenant membership and user roles

The RLS policies are implemented using PostgreSQL's RLS feature and custom security functions. 