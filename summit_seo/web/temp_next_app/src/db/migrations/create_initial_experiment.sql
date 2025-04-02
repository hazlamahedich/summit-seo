-- Create the initial dashboard widget design experiment
INSERT INTO ab_testing.ab_experiments (
  id,
  name, 
  description, 
  active, 
  start_date
) VALUES (
  '11111111-1111-1111-1111-111111111111', -- Fixed UUID for consistency in development
  'Dashboard Widget Design',
  'Test different visual styles for dashboard widgets to identify which drives the most engagement',
  true,
  NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Create three variants for the experiment
INSERT INTO ab_testing.ab_variants (
  experiment_id,
  name,
  weight
) VALUES 
  ('11111111-1111-1111-1111-111111111111', 'standard-design', 33),
  ('11111111-1111-1111-1111-111111111111', 'visual-design', 33),
  ('11111111-1111-1111-1111-111111111111', 'minimalist-design', 34)
ON CONFLICT DO NOTHING; 