-- Function to add an admin user directly by UUID
CREATE OR REPLACE FUNCTION ab_testing.add_admin_by_uuid(user_uuid UUID)
RETURNS UUID AS $$
DECLARE
  admin_id UUID;
BEGIN
  -- Insert the user as admin if not already an admin
  INSERT INTO ab_testing.admin_users (user_id)
  VALUES (user_uuid)
  ON CONFLICT (user_id) DO NOTHING
  RETURNING id INTO admin_id;
  
  RETURN admin_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Modify the RLS policy for the admin_users table so the first admin can be added
DROP POLICY IF EXISTS manage_admin_users ON ab_testing.admin_users;

-- If there are no admin users, allow the current user to become an admin
CREATE POLICY manage_admin_users ON ab_testing.admin_users
  FOR ALL USING (
    auth.uid() IN (SELECT user_id FROM ab_testing.admin_users)
    OR
    (SELECT COUNT(*) FROM ab_testing.admin_users) = 0
  );

-- Function to initialize the first admin user as the current user
CREATE OR REPLACE FUNCTION ab_testing.initialize_first_admin()
RETURNS UUID AS $$
DECLARE
  admin_id UUID;
BEGIN
  -- Exit if there are already admin users
  IF (SELECT COUNT(*) FROM ab_testing.admin_users) > 0 THEN
    RETURN NULL;
  END IF;

  -- Make the current user an admin
  INSERT INTO ab_testing.admin_users (user_id)
  VALUES (auth.uid())
  RETURNING id INTO admin_id;
  
  RETURN admin_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 