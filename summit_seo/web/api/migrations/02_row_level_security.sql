-- 02_row_level_security.sql
-- Row Level Security policies for Summit SEO

-- Enable RLS on all tables
ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE role ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE project ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE finding ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation ENABLE ROW LEVEL SECURITY;

-- Create helper function to check if a policy exists
CREATE OR REPLACE FUNCTION policy_exists(p_policy_name text, p_table_name text) 
RETURNS boolean AS $$
DECLARE
    exists_val boolean;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM pg_catalog.pg_policy 
        WHERE polname = p_policy_name 
        AND polrelid = (p_table_name::regclass)
    ) INTO exists_val;
    
    RETURN exists_val;
END;
$$ LANGUAGE plpgsql;

-- Create a function to check if user is an admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_roles ur
        JOIN role r ON ur.role_id = r.id
        WHERE ur.user_id = auth.uid() AND r.name = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user belongs to a tenant
CREATE OR REPLACE FUNCTION is_tenant_member(tenant_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tenant_user tu
        WHERE tu.tenant_id = tenant_id AND tu.user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user can manage a tenant
CREATE OR REPLACE FUNCTION can_manage_tenant(tenant_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tenant_user tu
        WHERE tu.tenant_id = tenant_id AND tu.user_id = auth.uid() 
        AND (tu.role = 'owner' OR tu.role = 'admin' OR tu.can_manage_users = TRUE)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user can manage projects in a tenant
CREATE OR REPLACE FUNCTION can_manage_projects(tenant_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tenant_user tu
        WHERE tu.tenant_id = tenant_id AND tu.user_id = auth.uid() 
        AND (tu.role = 'owner' OR tu.role = 'admin' OR tu.can_create_projects = TRUE)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user is tenant owner
CREATE OR REPLACE FUNCTION is_tenant_owner(tenant_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tenant t
        WHERE t.tenant_id = tenant_id AND t.owner_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply RLS policies for each table with existence checks
DO $$
BEGIN
    -- RLS policies for User table
    IF NOT policy_exists('user_self_access', 'user') THEN
        CREATE POLICY user_self_access ON "user"
            USING (id = auth.uid());
    END IF;

    IF NOT policy_exists('user_admin_access', 'user') THEN
        CREATE POLICY user_admin_access ON "user"
            USING (is_admin());
    END IF;

    -- RLS policies for Role table
    IF NOT policy_exists('role_all_read', 'role') THEN
        CREATE POLICY role_all_read ON role
            FOR SELECT USING (true);
    END IF;

    IF NOT policy_exists('role_admin_write', 'role') THEN
        CREATE POLICY role_admin_write ON role
            FOR ALL USING (is_admin());
    END IF;

    -- RLS policies for User Roles table
    IF NOT policy_exists('user_roles_self_read', 'user_roles') THEN
        CREATE POLICY user_roles_self_read ON user_roles
            FOR SELECT USING (user_id = auth.uid());
    END IF;

    IF NOT policy_exists('user_roles_admin_all', 'user_roles') THEN
        CREATE POLICY user_roles_admin_all ON user_roles
            USING (is_admin());
    END IF;

    -- RLS policies for Tenant table
    IF NOT policy_exists('tenant_member_read', 'tenant') THEN
        CREATE POLICY tenant_member_read ON tenant
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('tenant_owner_all', 'tenant') THEN
        CREATE POLICY tenant_owner_all ON tenant
            USING (owner_id = auth.uid());
    END IF;

    IF NOT policy_exists('tenant_admin_all', 'tenant') THEN
        CREATE POLICY tenant_admin_all ON tenant
            USING (is_admin());
    END IF;

    -- RLS policies for Tenant User table
    IF NOT policy_exists('tenant_user_member_read', 'tenant_user') THEN
        CREATE POLICY tenant_user_member_read ON tenant_user
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('tenant_user_manage', 'tenant_user') THEN
        CREATE POLICY tenant_user_manage ON tenant_user
            FOR ALL USING (can_manage_tenant(tenant_id));
    END IF;

    IF NOT policy_exists('tenant_user_admin_all', 'tenant_user') THEN
        CREATE POLICY tenant_user_admin_all ON tenant_user
            USING (is_admin());
    END IF;

    -- RLS policies for Project table
    IF NOT policy_exists('project_tenant_member_read', 'project') THEN
        CREATE POLICY project_tenant_member_read ON project
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('project_tenant_manager_write', 'project') THEN
        CREATE POLICY project_tenant_manager_write ON project
            FOR INSERT WITH CHECK (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('project_tenant_manager_update', 'project') THEN
        CREATE POLICY project_tenant_manager_update ON project
            FOR UPDATE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('project_tenant_manager_delete', 'project') THEN
        CREATE POLICY project_tenant_manager_delete ON project
            FOR DELETE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('project_admin_all', 'project') THEN
        CREATE POLICY project_admin_all ON project
            USING (is_admin());
    END IF;

    -- RLS policies for Analysis table
    IF NOT policy_exists('analysis_tenant_member_read', 'analysis') THEN
        CREATE POLICY analysis_tenant_member_read ON analysis
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('analysis_tenant_manager_write', 'analysis') THEN
        CREATE POLICY analysis_tenant_manager_write ON analysis
            FOR INSERT WITH CHECK (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('analysis_tenant_manager_update', 'analysis') THEN
        CREATE POLICY analysis_tenant_manager_update ON analysis
            FOR UPDATE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('analysis_tenant_manager_delete', 'analysis') THEN
        CREATE POLICY analysis_tenant_manager_delete ON analysis
            FOR DELETE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('analysis_admin_all', 'analysis') THEN
        CREATE POLICY analysis_admin_all ON analysis
            USING (is_admin());
    END IF;

    -- RLS policies for Finding table
    IF NOT policy_exists('finding_tenant_member_read', 'finding') THEN
        CREATE POLICY finding_tenant_member_read ON finding
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('finding_tenant_manager_write', 'finding') THEN
        CREATE POLICY finding_tenant_manager_write ON finding
            FOR INSERT WITH CHECK (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('finding_tenant_manager_update', 'finding') THEN
        CREATE POLICY finding_tenant_manager_update ON finding
            FOR UPDATE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('finding_tenant_manager_delete', 'finding') THEN
        CREATE POLICY finding_tenant_manager_delete ON finding
            FOR DELETE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('finding_admin_all', 'finding') THEN
        CREATE POLICY finding_admin_all ON finding
            USING (is_admin());
    END IF;

    -- RLS policies for Recommendation table
    IF NOT policy_exists('recommendation_tenant_member_read', 'recommendation') THEN
        CREATE POLICY recommendation_tenant_member_read ON recommendation
            FOR SELECT USING (is_tenant_member(tenant_id));
    END IF;

    IF NOT policy_exists('recommendation_tenant_manager_write', 'recommendation') THEN
        CREATE POLICY recommendation_tenant_manager_write ON recommendation
            FOR INSERT WITH CHECK (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('recommendation_tenant_manager_update', 'recommendation') THEN
        CREATE POLICY recommendation_tenant_manager_update ON recommendation
            FOR UPDATE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('recommendation_tenant_manager_delete', 'recommendation') THEN
        CREATE POLICY recommendation_tenant_manager_delete ON recommendation
            FOR DELETE USING (can_manage_projects(tenant_id));
    END IF;

    IF NOT policy_exists('recommendation_admin_all', 'recommendation') THEN
        CREATE POLICY recommendation_admin_all ON recommendation
            USING (is_admin());
    END IF;
END$$; 