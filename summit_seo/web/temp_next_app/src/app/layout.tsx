import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "@/styles/tour.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Navbar } from "@/components/ui/navbar";
import { ReactQueryProvider } from "@/providers/react-query-provider";
import { AuthProvider } from "@/providers/auth-provider";
import { ResponsiveProvider } from "@/contexts/responsive-context";
import { ResponsiveDebugger } from "@/components/ui/responsive-debugger";
import { KeyboardShortcutsProvider } from "@/contexts/keyboard-shortcuts-context";
import { SoundEffectsProvider } from "@/contexts/sound-effects-context";
import { TourNotification } from "@/components/onboarding/tour-notification";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Summit SEO - Advanced SEO Analysis Tool",
  description: "Comprehensive SEO analysis and optimization tool for websites of all sizes.",
  manifest: "/manifest.json",
  themeColor: "#0ea5e9",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Summit SEO",
  },
  formatDetection: {
    telephone: false,
  },
  applicationName: "Summit SEO",
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ResponsiveProvider>
            <SoundEffectsProvider>
              <KeyboardShortcutsProvider>
                <AuthProvider>
                  <ReactQueryProvider>
                    <div className="flex min-h-screen flex-col">
                      {/* Header */}
                      <Navbar 
                        logo={<h1 className="text-xl font-bold">Summit SEO</h1>}
                        sticky
                      >
                        <Button variant="ghost" asChild>
                          <Link href="/auth/login">Login</Link>
                        </Button>
                        <Button variant="default" asChild>
                          <Link href="/auth/register">Sign Up</Link>
                        </Button>
                      </Navbar>
                      
                      {/* Main content */}
                      <main className="flex-grow">{children}</main>
                      
                      {/* Footer */}
                      <footer className="border-t py-6 md:py-0">
                        <div className="container px-4 md:px-6">
                          <div className="grid grid-cols-1 gap-8 md:grid-cols-4 lg:gap-12">
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Features</h3>
                              <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:underline">SEO Analyzer</a></li>
                                <li><a href="#" className="hover:underline">Keyword Research</a></li>
                                <li><a href="#" className="hover:underline">Backlink Analysis</a></li>
                                <li><a href="#" className="hover:underline">Content Optimization</a></li>
                              </ul>
                            </div>
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Resources</h3>
                              <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:underline">Documentation</a></li>
                                <li><a href="#" className="hover:underline">Blog</a></li>
                                <li><a href="#" className="hover:underline">Guides</a></li>
                                <li><a href="#" className="hover:underline">API Reference</a></li>
                              </ul>
                            </div>
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Company</h3>
                              <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:underline">About</a></li>
                                <li><a href="#" className="hover:underline">Careers</a></li>
                                <li><a href="#" className="hover:underline">Contact</a></li>
                                <li><a href="#" className="hover:underline">Press</a></li>
                              </ul>
                            </div>
                            <div className="space-y-4">
                              <h3 className="text-lg font-medium">Legal</h3>
                              <ul className="space-y-2 text-sm">
                                <li><a href="#" className="hover:underline">Terms</a></li>
                                <li><a href="#" className="hover:underline">Privacy</a></li>
                                <li><a href="#" className="hover:underline">Cookies</a></li>
                                <li><a href="#" className="hover:underline">Licenses</a></li>
                              </ul>
                            </div>
                          </div>
                          <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
                            © {new Date().getFullYear()} Summit SEO. All rights reserved.
                          </div>
                        </div>
                      </footer>
                      
                      {/* Tour notification */}
                      <TourNotification />
                      
                      {/* Responsive debugger - only in development */}
                      {process.env.NODE_ENV === "development" && (
                        <ResponsiveDebugger />
                      )}
                    </div>
                  </ReactQueryProvider>
                </AuthProvider>
              </KeyboardShortcutsProvider>
            </SoundEffectsProvider>
          </ResponsiveProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
