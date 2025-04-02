// Script to create test users in Supabase
const { createClient } = require('@supabase/supabase-js');

// You'll need to replace this with your actual service role key
// IMPORTANT: Never commit this key to version control!
// Get it from the Supabase dashboard > Project settings > API
const supabaseUrl = process.env.SUPABASE_URL || 'https://gqbihjuxgutbxsqfhxnd.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

if (!supabaseServiceKey) {
  console.error('Error: SUPABASE_SERVICE_ROLE_KEY environment variable is required');
  console.error('Get this from Supabase dashboard > Project settings > API > service_role key');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function createTestUsers() {
  try {
    console.log('Creating test users...');
    
    // Create admin user
    const { data: adminData, error: adminError } = await supabase.auth.admin.createUser({
      email: 'admin@example.com',
      password: 'Admin123!',
      email_confirm: true,
      user_metadata: { 
        full_name: 'Admin User',
        is_admin: true
      }
    });
    
    if (adminError) {
      console.error('Error creating admin user:', adminError);
    } else {
      console.log('Admin user created successfully:', adminData.user.email);
      console.log('Admin user ID:', adminData.user.id);
      
      // Insert into custom user table if needed
      const { error: adminProfileError } = await supabase
        .from('user')
        .upsert({
          id: adminData.user.id,
          created_at: new Date(),
          updated_at: new Date(),
          is_deleted: false,
          email: adminData.user.email,
          username: 'admin',
          first_name: 'Admin',
          last_name: 'User',
          password_hash: '', // Auth handled by Supabase
          is_active: true,
          is_verified: true,
          profile_picture_url: null
        });
        
      if (adminProfileError) {
        console.error('Error creating admin profile:', adminProfileError);
      } else {
        console.log('Admin profile created successfully');
      }
    }

    // Create regular test user
    const { data: userData, error: userError } = await supabase.auth.admin.createUser({
      email: 'user@example.com',
      password: 'User123!',
      email_confirm: true,
      user_metadata: { 
        full_name: 'Test User'
      }
    });
    
    if (userError) {
      console.error('Error creating test user:', userError);
    } else {
      console.log('Test user created successfully:', userData.user.email);
      console.log('Test user ID:', userData.user.id);
      
      // Insert into custom user table if needed
      const { error: userProfileError } = await supabase
        .from('user')
        .upsert({
          id: userData.user.id,
          created_at: new Date(),
          updated_at: new Date(),
          is_deleted: false,
          email: userData.user.email,
          username: 'testuser',
          first_name: 'Test',
          last_name: 'User',
          password_hash: '', // Auth handled by Supabase
          is_active: true,
          is_verified: true,
          profile_picture_url: null
        });
        
      if (userProfileError) {
        console.error('Error creating user profile:', userProfileError);
      } else {
        console.log('User profile created successfully');
      }
    }

    console.log('\nTest Users Summary:');
    console.log('------------------');
    console.log('Admin User:');
    console.log('  Email: admin@example.com');
    console.log('  Password: Admin123!');
    console.log('\nRegular User:');
    console.log('  Email: user@example.com');
    console.log('  Password: User123!');
    console.log('\nYou can now log in with these credentials in your application.');

  } catch (error) {
    console.error('Unexpected error creating test users:', error);
  }
}

createTestUsers(); 