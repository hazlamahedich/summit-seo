#!/bin/bash

# Make sure you have Node.js installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

# Check if @supabase/supabase-js is installed
if ! npm list @supabase/supabase-js &> /dev/null; then
    echo "Installing @supabase/supabase-js..."
    npm install @supabase/supabase-js
fi

# Prompt for the Supabase service role key if not provided
if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    read -p "Enter your Supabase service role key: " service_key
    
    if [ -z "$service_key" ]; then
        echo "Error: Supabase service role key is required."
        echo "You can find it in Supabase dashboard > Project Settings > API > service_role key"
        exit 1
    fi
else
    service_key=$SUPABASE_SERVICE_ROLE_KEY
fi

# Set the environment variables and run the script
SUPABASE_URL=https://gqbihjuxgutbxsqfhxnd.supabase.co \
SUPABASE_SERVICE_ROLE_KEY=$service_key \
node ./scripts/create-test-users.js 