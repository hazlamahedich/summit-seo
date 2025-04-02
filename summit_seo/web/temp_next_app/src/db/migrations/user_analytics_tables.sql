-- Create schema for user behavior analytics
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create user events table
CREATE TABLE IF NOT EXISTS analytics.user_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_category TEXT NOT NULL,
  event_action TEXT NOT NULL,
  event_label TEXT,
  event_value JSONB,
  page_path TEXT,
  page_title TEXT,
  client_timestamp TIMESTAMPTZ NOT NULL,
  server_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  session_id TEXT,
  device_type TEXT,
  browser TEXT,
  os TEXT,
  screen_size TEXT,
  referrer TEXT
);

-- Create user sessions table
CREATE TABLE IF NOT EXISTS analytics.user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  end_time TIMESTAMPTZ,
  duration INTEGER, -- in seconds
  device_type TEXT,
  browser TEXT,
  os TEXT,
  screen_size TEXT,
  entry_page TEXT,
  exit_page TEXT,
  page_views INTEGER DEFAULT 1,
  events_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true
);

-- Create feature usage table
CREATE TABLE IF NOT EXISTS analytics.feature_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  feature_id TEXT NOT NULL,
  feature_category TEXT NOT NULL,
  first_used TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_used TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  usage_count INTEGER NOT NULL DEFAULT 1,
  UNIQUE(user_id, feature_id)
);

-- Create heatmap data table
CREATE TABLE IF NOT EXISTS analytics.heatmap_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  page_path TEXT NOT NULL,
  event_type TEXT NOT NULL, -- click, move, scroll
  position_x INTEGER,
  position_y INTEGER,
  scroll_depth INTEGER, -- percentage of page scrolled
  viewport_width INTEGER,
  viewport_height INTEGER,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_user_events_user_id ON analytics.user_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_events_event_type ON analytics.user_events(event_type);
CREATE INDEX IF NOT EXISTS idx_user_events_event_category ON analytics.user_events(event_category);
CREATE INDEX IF NOT EXISTS idx_user_events_page_path ON analytics.user_events(page_path);
CREATE INDEX IF NOT EXISTS idx_user_events_client_timestamp ON analytics.user_events(client_timestamp);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON analytics.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON analytics.user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_start_time ON analytics.user_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON analytics.user_sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_feature_usage_user_id ON analytics.feature_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_feature_usage_feature_id ON analytics.feature_usage(feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_usage_feature_category ON analytics.feature_usage(feature_category);

CREATE INDEX IF NOT EXISTS idx_heatmap_data_user_id ON analytics.heatmap_data(user_id);
CREATE INDEX IF NOT EXISTS idx_heatmap_data_page_path ON analytics.heatmap_data(page_path);
CREATE INDEX IF NOT EXISTS idx_heatmap_data_event_type ON analytics.heatmap_data(event_type);

-- Create RLS policies for user events table
ALTER TABLE analytics.user_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY insert_user_events ON analytics.user_events
  FOR INSERT WITH CHECK (auth.uid() = user_id);
  
CREATE POLICY view_own_user_events ON analytics.user_events
  FOR SELECT USING (auth.uid() = user_id);
  
CREATE POLICY view_all_user_events ON analytics.user_events
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));

-- Create RLS policies for user sessions table
ALTER TABLE analytics.user_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY insert_user_sessions ON analytics.user_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY update_user_sessions ON analytics.user_sessions
  FOR UPDATE USING (auth.uid() = user_id);
  
CREATE POLICY view_own_user_sessions ON analytics.user_sessions
  FOR SELECT USING (auth.uid() = user_id);
  
CREATE POLICY view_all_user_sessions ON analytics.user_sessions
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));

-- Create RLS policies for feature usage table
ALTER TABLE analytics.feature_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY insert_feature_usage ON analytics.feature_usage
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY update_feature_usage ON analytics.feature_usage
  FOR UPDATE USING (auth.uid() = user_id);
  
CREATE POLICY view_own_feature_usage ON analytics.feature_usage
  FOR SELECT USING (auth.uid() = user_id);
  
CREATE POLICY view_all_feature_usage ON analytics.feature_usage
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));

-- Create RLS policies for heatmap data table
ALTER TABLE analytics.heatmap_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY insert_heatmap_data ON analytics.heatmap_data
  FOR INSERT WITH CHECK (auth.uid() = user_id);
  
CREATE POLICY view_own_heatmap_data ON analytics.heatmap_data
  FOR SELECT USING (auth.uid() = user_id);
  
CREATE POLICY view_all_heatmap_data ON analytics.heatmap_data
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));

-- Create analytics admins table
CREATE TABLE IF NOT EXISTS analytics.analytics_admins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Create RLS policies for analytics admins table
ALTER TABLE analytics.analytics_admins ENABLE ROW LEVEL SECURITY;

CREATE POLICY view_analytics_admins ON analytics.analytics_admins
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));
  
CREATE POLICY manage_analytics_admins ON analytics.analytics_admins
  FOR ALL USING (auth.uid() IN (
    SELECT user_id FROM analytics.analytics_admins
  ));

-- Function to add an analytics admin
CREATE OR REPLACE FUNCTION analytics.add_analytics_admin(user_email TEXT)
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
  INSERT INTO analytics.analytics_admins (user_id)
  VALUES (user_id)
  ON CONFLICT (user_id) DO NOTHING
  RETURNING id INTO admin_id;
  
  RETURN admin_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update feature usage
CREATE OR REPLACE FUNCTION analytics.track_feature_usage(
  p_user_id UUID,
  p_feature_id TEXT,
  p_feature_category TEXT
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO analytics.feature_usage (user_id, feature_id, feature_category)
  VALUES (p_user_id, p_feature_id, p_feature_category)
  ON CONFLICT (user_id, feature_id) 
  DO UPDATE SET 
    last_used = NOW(),
    usage_count = analytics.feature_usage.usage_count + 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update or create user session
CREATE OR REPLACE FUNCTION analytics.update_user_session(
  p_user_id UUID,
  p_session_id TEXT,
  p_page_path TEXT,
  p_device_type TEXT DEFAULT NULL,
  p_browser TEXT DEFAULT NULL,
  p_os TEXT DEFAULT NULL,
  p_screen_size TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  session_id UUID;
BEGIN
  -- Check if session exists
  SELECT id INTO session_id FROM analytics.user_sessions 
  WHERE user_id = p_user_id AND session_id = p_session_id AND is_active = true;
  
  IF session_id IS NULL THEN
    -- Create new session
    INSERT INTO analytics.user_sessions 
      (user_id, session_id, entry_page, device_type, browser, os, screen_size)
    VALUES 
      (p_user_id, p_session_id, p_page_path, p_device_type, p_browser, p_os, p_screen_size)
    RETURNING id INTO session_id;
  ELSE
    -- Update existing session
    UPDATE analytics.user_sessions 
    SET 
      exit_page = p_page_path,
      page_views = page_views + 1,
      end_time = NOW(),
      duration = EXTRACT(EPOCH FROM (NOW() - start_time))::INTEGER
    WHERE id = session_id;
  END IF;
  
  RETURN session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 