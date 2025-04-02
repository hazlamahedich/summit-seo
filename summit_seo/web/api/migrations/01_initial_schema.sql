-- 01_initial_schema.sql
-- Initial schema creation for Summit SEO

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types first (before table creation)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'analysis_status') THEN
        CREATE TYPE analysis_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severity_level') THEN
        CREATE TYPE severity_level AS ENUM ('critical', 'high', 'medium', 'low', 'info');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_type') THEN
        CREATE TYPE recommendation_type AS ENUM ('best_practice', 'quick_win', 'technical', 'content', 'security', 'performance');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_priority') THEN
        CREATE TYPE recommendation_priority AS ENUM ('critical', 'high', 'medium', 'low');
    END IF;
END$$;

-- Role Table
CREATE TABLE IF NOT EXISTS role (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- User Table
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    profile_picture_url VARCHAR(255)
);

-- User Roles Association Table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
    role_id UUID REFERENCES role(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Tenant Table
CREATE TABLE IF NOT EXISTS tenant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    subdomain VARCHAR(50) UNIQUE,
    owner_id UUID NOT NULL REFERENCES "user"(id),
    logo_url VARCHAR(255),
    primary_color VARCHAR(10),
    secondary_color VARCHAR(10)
);

-- Tenant User Association Table
CREATE TABLE IF NOT EXISTS tenant_user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL REFERENCES "user"(id),
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    can_create_projects BOOLEAN NOT NULL DEFAULT FALSE,
    can_delete_projects BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_users BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (tenant_id, user_id)
);

-- Project Table
CREATE TABLE IF NOT EXISTS project (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    url VARCHAR(512) NOT NULL,
    settings JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    icon_url VARCHAR(255),
    last_score FLOAT,
    score_change FLOAT,
    issues_count INTEGER DEFAULT 0,
    critical_issues_count INTEGER DEFAULT 0
);

-- Analysis Table
CREATE TABLE IF NOT EXISTS analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    status analysis_status NOT NULL DEFAULT 'pending',
    project_id UUID NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    config JSONB,
    score FLOAT,
    results JSONB,
    started_at FLOAT,
    completed_at FLOAT,
    duration FLOAT,
    error TEXT,
    error_details JSONB,
    analyzer_versions JSONB,
    issues_count INTEGER DEFAULT 0,
    critical_issues_count INTEGER DEFAULT 0,
    high_issues_count INTEGER DEFAULT 0,
    medium_issues_count INTEGER DEFAULT 0,
    low_issues_count INTEGER DEFAULT 0
);

-- Finding Table
CREATE TABLE IF NOT EXISTS finding (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    analysis_id UUID NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    analyzer VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity severity_level NOT NULL,
    locations JSONB,
    metadata JSONB
);

-- Recommendation Table
CREATE TABLE IF NOT EXISTS recommendation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    tenant_id UUID NOT NULL,
    analysis_id UUID NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    finding_id UUID REFERENCES finding(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty INTEGER,
    impact INTEGER,
    priority recommendation_priority NOT NULL,
    type recommendation_type NOT NULL,
    implementation TEXT,
    code_examples JSONB,
    resources JSONB,
    estimated_time INTEGER
);

-- Indexes for performance optimization
-- Create a function to check if an index exists before creating it
DO $$
BEGIN
    -- User table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_email') THEN
        CREATE INDEX idx_user_email ON "user" (email);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_username') THEN
        CREATE INDEX idx_user_username ON "user" (username);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_is_deleted') THEN
        CREATE INDEX idx_user_is_deleted ON "user" (is_deleted);
    END IF;
    
    -- Role table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_role_name') THEN
        CREATE INDEX idx_role_name ON role (name);
    END IF;
    
    -- Tenant table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tenant_owner') THEN
        CREATE INDEX idx_tenant_owner ON tenant (owner_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tenant_is_deleted') THEN
        CREATE INDEX idx_tenant_is_deleted ON tenant (is_deleted);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tenant_id') THEN
        CREATE INDEX idx_tenant_id ON tenant (tenant_id);
    END IF;
    
    -- Project table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_project_tenant') THEN
        CREATE INDEX idx_project_tenant ON project (tenant_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_project_is_deleted') THEN
        CREATE INDEX idx_project_is_deleted ON project (is_deleted);
    END IF;
    
    -- Analysis table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_analysis_project') THEN
        CREATE INDEX idx_analysis_project ON analysis (project_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_analysis_tenant') THEN
        CREATE INDEX idx_analysis_tenant ON analysis (tenant_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_analysis_status') THEN
        CREATE INDEX idx_analysis_status ON analysis (status);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_analysis_is_deleted') THEN
        CREATE INDEX idx_analysis_is_deleted ON analysis (is_deleted);
    END IF;
    
    -- Finding table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_finding_analysis') THEN
        CREATE INDEX idx_finding_analysis ON finding (analysis_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_finding_tenant') THEN
        CREATE INDEX idx_finding_tenant ON finding (tenant_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_finding_severity') THEN
        CREATE INDEX idx_finding_severity ON finding (severity);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_finding_is_deleted') THEN
        CREATE INDEX idx_finding_is_deleted ON finding (is_deleted);
    END IF;
    
    -- Recommendation table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_analysis') THEN
        CREATE INDEX idx_recommendation_analysis ON recommendation (analysis_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_finding') THEN
        CREATE INDEX idx_recommendation_finding ON recommendation (finding_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_tenant') THEN
        CREATE INDEX idx_recommendation_tenant ON recommendation (tenant_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_is_deleted') THEN
        CREATE INDEX idx_recommendation_is_deleted ON recommendation (is_deleted);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_priority') THEN
        CREATE INDEX idx_recommendation_priority ON recommendation (priority);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_recommendation_type') THEN
        CREATE INDEX idx_recommendation_type ON recommendation (type);
    END IF;
END$$;

-- Set up Row Level Security later after table creation 