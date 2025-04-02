'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/auth/protected-route';

export default function ProjectsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  );
} 