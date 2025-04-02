import React from 'react';
import { Metadata } from 'next';
import AnalyticsDashboard from '@/components/analytics/analytics-dashboard';

export const metadata: Metadata = {
  title: 'User Behavior Analytics | Summit SEO Admin',
  description: 'Track and analyze user behavior patterns to optimize user experience.',
};

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto py-6">
      <AnalyticsDashboard />
    </div>
  );
} 