-- Create a special function to create the first admin user without auth checks
-- This should be run with admin privileges (service role)

-- Create a special function to add a new user and make them an admin
CREATE OR REPLACE FUNCTION ab_testing.bootstrap_admin_user(admin_email TEXT, admin_password TEXT)
RETURNS JSONB AS $$
DECLARE
  new_user_id UUID;
  admin_id UUID;
  result JSONB;
BEGIN
  -- First create a new user in auth.users (Service Role required)
  -- This is just for bootstrapping and testing - in production you'd use Supabase Auth UI
  
  -- Create the user (simplified - in production use proper auth flows)
  INSERT INTO auth.users (email, encrypted_password, email_confirmed_at, confirmation_sent_at)
  VALUES (
    admin_email, 
    crypt(admin_password, gen_salt('bf')), 
    now(), 
    now()
  )
  RETURNING id INTO new_user_id;
  
  -- Make the new user an admin
  INSERT INTO ab_testing.admin_users (user_id)
  VALUES (new_user_id)
  RETURNING id INTO admin_id;
  
  -- Return success info
  result := jsonb_build_object(
    'success', true,
    'user_id', new_user_id,
    'admin_id', admin_id,
    'email', admin_email
  );
  
  RETURN result;
EXCEPTION
  WHEN OTHERS THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', SQLERRM
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Alternative version - direct insert without using auth tables
CREATE OR REPLACE FUNCTION ab_testing.create_initial_admin(admin_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- Insert directly into admin_users
  -- Warning: This bypasses all security checks and should only be used for initial setup
  INSERT INTO ab_testing.admin_users (user_id, id)
  VALUES (admin_id, admin_id)
  ON CONFLICT DO NOTHING;
  
  -- Check if successful
  RETURN EXISTS (SELECT 1 FROM ab_testing.admin_users WHERE user_id = admin_id);
END;
$$ LANGUAGE plpgsql; 