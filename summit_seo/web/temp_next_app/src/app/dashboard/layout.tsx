'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { UserPreferencesProvider } from '@/contexts/user-preferences-context';
import { ABTestingProvider } from '@/contexts/ab-testing-context';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <ABTestingProvider>
        <UserPreferencesProvider>
          {children}
        </UserPreferencesProvider>
      </ABTestingProvider>
    </ProtectedRoute>
  );
} 