'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If auth is not loading and user is not authenticated, redirect to login
    if (!isLoading && !user) {
      router.push('/auth/login?redirect=' + encodeURIComponent(window.location.pathname));
    }
  }, [user, isLoading, router]);

  // While loading, show a minimal loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-primary/30 border-t-primary animate-spin"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, show nothing (will redirect via useEffect)
  if (!user) {
    return null;
  }

  // If authenticated, render children
  return <>{children}</>;
} 