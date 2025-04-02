-- Create schema for A/B testing
CREATE SCHEMA IF NOT EXISTS ab_testing;

-- Create experiments table
CREATE TABLE IF NOT EXISTS ab_testing.ab_experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  active BOOLEAN NOT NULL DEFAULT true,
  start_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  end_date TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create variants table
CREATE TABLE IF NOT EXISTS ab_testing.ab_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID NOT NULL REFERENCES ab_testing.ab_experiments(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  weight INTEGER NOT NULL DEFAULT 50, -- percentage weight (0-100)
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create user experiment assignments table
CREATE TABLE IF NOT EXISTS ab_testing.ab_user_experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  experiment_id UUID NOT NULL REFERENCES ab_testing.ab_experiments(id) ON DELETE CASCADE,
  variant_id UUID NOT NULL REFERENCES ab_testing.ab_variants(id) ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_interaction TIMESTAMPTZ,
  interactions INTEGER NOT NULL DEFAULT 0,
  converted BOOLEAN NOT NULL DEFAULT false,
  UNIQUE(user_id, experiment_id)
);

-- Create admin users table for managing admin access
CREATE TABLE IF NOT EXISTS ab_testing.admin_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_ab_experiments_active ON ab_testing.ab_experiments(active);
CREATE INDEX IF NOT EXISTS idx_ab_variants_experiment_id ON ab_testing.ab_variants(experiment_id);
CREATE INDEX IF NOT EXISTS idx_ab_user_experiments_user_id ON ab_testing.ab_user_experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_user_experiments_experiment_id ON ab_testing.ab_user_experiments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_ab_user_experiments_variant_id ON ab_testing.ab_user_experiments(variant_id);
CREATE INDEX IF NOT EXISTS idx_admin_users_user_id ON ab_testing.admin_users(user_id);

-- Create RLS policies for experiments table
ALTER TABLE ab_testing.ab_experiments ENABLE ROW LEVEL SECURITY;

CREATE POLICY view_experiments ON ab_testing.ab_experiments
  FOR SELECT USING (true);
  
CREATE POLICY insert_experiments ON ab_testing.ab_experiments
  FOR INSERT WITH CHECK (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY update_experiments ON ab_testing.ab_experiments
  FOR UPDATE USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY delete_experiments ON ab_testing.ab_experiments
  FOR DELETE USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );

-- Create RLS policies for variants table
ALTER TABLE ab_testing.ab_variants ENABLE ROW LEVEL SECURITY;

CREATE POLICY view_variants ON ab_testing.ab_variants
  FOR SELECT USING (true);
  
CREATE POLICY insert_variants ON ab_testing.ab_variants
  FOR INSERT WITH CHECK (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY update_variants ON ab_testing.ab_variants
  FOR UPDATE USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY delete_variants ON ab_testing.ab_variants
  FOR DELETE USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );

-- Create RLS policies for user experiment assignments table
ALTER TABLE ab_testing.ab_user_experiments ENABLE ROW LEVEL SECURITY;

CREATE POLICY view_user_experiments ON ab_testing.ab_user_experiments
  FOR SELECT USING (
    auth.uid() = user_id OR 
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY insert_user_experiments ON ab_testing.ab_user_experiments
  FOR INSERT WITH CHECK (auth.uid() = user_id);
  
CREATE POLICY update_user_experiments ON ab_testing.ab_user_experiments
  FOR UPDATE USING (
    auth.uid() = user_id OR 
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );

-- Create RLS policies for admin users table
ALTER TABLE ab_testing.admin_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY view_admin_users ON ab_testing.admin_users
  FOR SELECT USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );
  
CREATE POLICY manage_admin_users ON ab_testing.admin_users
  FOR ALL USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
  );

-- Add function to update updated_at timestamp
CREATE OR REPLACE FUNCTION ab_testing.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers to update updated_at
CREATE TRIGGER update_ab_experiments_timestamp
BEFORE UPDATE ON ab_testing.ab_experiments
FOR EACH ROW EXECUTE FUNCTION ab_testing.update_modified_column();

CREATE TRIGGER update_ab_variants_timestamp
BEFORE UPDATE ON ab_testing.ab_variants
FOR EACH ROW EXECUTE FUNCTION ab_testing.update_modified_column();

-- Helper function to add an admin user
CREATE OR REPLACE FUNCTION ab_testing.add_admin_user(user_email TEXT)
RETURNS UUID AS $$
DECLARE
  user_id UUID;
  admin_id UUID;
BEGIN
  -- Find the user ID from the email
  SELECT id INTO user_id FROM auth.users WHERE email = user_email;
  
  IF user_id IS NULL THEN
    RAISE EXCEPTION 'User with email % not found', user_email;
  END IF;
  
  -- Insert the user as admin if not already an admin
  INSERT INTO ab_testing.admin_users (user_id)
  VALUES (user_id)
  ON CONFLICT (user_id) DO NOTHING
  RETURNING id INTO admin_id;
  
  RETURN admin_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 