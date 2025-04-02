-- Simplify RLS policies for development/testing
-- NOTE: This is for development purposes only. In production, use proper admin-based security.

-- Drop existing policies
DROP POLICY IF EXISTS view_experiments ON ab_testing.ab_experiments;
DROP POLICY IF EXISTS insert_experiments ON ab_testing.ab_experiments;
DROP POLICY IF EXISTS update_experiments ON ab_testing.ab_experiments;
DROP POLICY IF EXISTS delete_experiments ON ab_testing.ab_experiments;

DROP POLICY IF EXISTS view_variants ON ab_testing.ab_variants;
DROP POLICY IF EXISTS insert_variants ON ab_testing.ab_variants;
DROP POLICY IF EXISTS update_variants ON ab_testing.ab_variants;
DROP POLICY IF EXISTS delete_variants ON ab_testing.ab_variants;

DROP POLICY IF EXISTS view_user_experiments ON ab_testing.ab_user_experiments;
DROP POLICY IF EXISTS insert_user_experiments ON ab_testing.ab_user_experiments;
DROP POLICY IF EXISTS update_user_experiments ON ab_testing.ab_user_experiments;

DROP POLICY IF EXISTS view_admin_users ON ab_testing.admin_users;
DROP POLICY IF EXISTS manage_admin_users ON ab_testing.admin_users;

-- Create simplified policies for development that allow authenticated users to do everything
-- Experiments table
CREATE POLICY dev_experiments_policy ON ab_testing.ab_experiments
  FOR ALL USING (auth.uid() IS NOT NULL);

-- Variants table  
CREATE POLICY dev_variants_policy ON ab_testing.ab_variants
  FOR ALL USING (auth.uid() IS NOT NULL);

-- User experiments table
CREATE POLICY dev_user_experiments_policy ON ab_testing.ab_user_experiments
  FOR ALL USING (auth.uid() IS NOT NULL);

-- Admin users table  
CREATE POLICY dev_admin_users_policy ON ab_testing.admin_users
  FOR ALL USING (auth.uid() IS NOT NULL);

-- Create a system-generated UUID to use for anonymous operations during development
CREATE OR REPLACE FUNCTION ab_testing.get_dev_user_id()
RETURNS UUID AS $$
BEGIN
  -- This is a fixed UUID used for development
  RETURN '00000000-0000-0000-0000-000000000000'::UUID;
END;
$$ LANGUAGE plpgsql; 