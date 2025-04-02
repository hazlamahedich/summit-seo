import React from 'react';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">      
      <main className="flex-1 flex items-center justify-center">
        {children}
      </main>
      
      <footer className="py-6 border-t">
        <div className="container text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Summit SEO. All rights reserved.
        </div>
      </footer>
    </div>
  );
} 