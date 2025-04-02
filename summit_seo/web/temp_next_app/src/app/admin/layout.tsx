'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { useAuth } from '@/providers/auth-provider';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  return (
    <ProtectedRoute>
      {isAdmin ? (
        children
      ) : (
        <div className="container mx-auto py-8">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Access Denied</AlertTitle>
            <AlertDescription>
              You don't have permission to access the admin dashboard. This area is restricted to administrators only.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </ProtectedRoute>
  );
} 