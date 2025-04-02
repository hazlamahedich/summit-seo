"use client";

import React from "react";
import { 
  Responsive, 
} from "@/components/ui/responsive";
import { Container } from "@/components/ui/container";
import { Grid } from "@/components/ui/grid";
import { Flex } from "@/components/ui/flex";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useResponsive } from "@/contexts/responsive-context";
import { ResponsiveDebugger } from "@/components/ui/responsive-debugger";
import { MobileNav } from "@/components/ui/mobile-nav";
import { PhoneIcon, TabletIcon, LaptopIcon, MonitorIcon } from "lucide-react";

export default function ResponsiveExamplePage() {
  const { 
    breakpoint, 
    deviceType, 
    isMobile, 
    isTablet, 
    isDesktop,
    windowSize 
  } = useResponsive();

  return (
    <Container>
      <div className="space-y-12 py-8">
        <section>
          <h1 className="text-4xl font-bold mb-4">Responsive Design Example</h1>
          <p className="text-lg text-muted-foreground mb-8">
            A demonstration of our responsive design system for all screen sizes
          </p>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Current Device Information</h2>
          <Card className="p-6">
            <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt className="font-medium text-muted-foreground">Breakpoint</dt>
                <dd className="mt-1 text-2xl font-semibold">{breakpoint}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Device Type</dt>
                <dd className="mt-1 text-2xl font-semibold">{deviceType}</dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Dimensions</dt>
                <dd className="mt-1 text-2xl font-semibold">
                  {windowSize.width} × {windowSize.height}
                </dd>
              </div>
              <div>
                <dt className="font-medium text-muted-foreground">Device Class</dt>
                <dd className="mt-1 text-2xl font-semibold">
                  {isMobile ? "Mobile 📱" : isTablet ? "Tablet 📊" : "Desktop 🖥️"}
                </dd>
              </div>
            </dl>
          </Card>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Responsive Grid Example</h2>
          <p className="text-muted-foreground">
            This grid adapts from 1 column on mobile to 4 columns on desktop
          </p>
          
          <Grid 
            cols={{
              default: 1,
              sm: 2,
              md: 3,
              lg: 4
            }} 
            gap={4}
          >
            {Array.from({ length: 8 }).map((_, i) => (
              <Card key={i} className="p-6 flex flex-col items-center justify-center aspect-square">
                <span className="text-2xl font-bold">{i + 1}</span>
                <span className="text-muted-foreground text-sm">Grid Item</span>
              </Card>
            ))}
          </Grid>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Conditional Content</h2>
          
          <div className="space-y-8">
            {/* Show specific content for different breakpoints */}
            <div className="space-y-6">
              <h3 className="text-xl font-medium">Using Breakpoint Components</h3>
              
              <div className="space-y-4">
                <Responsive.Show breakpoint="xs" above={false}>
                  <Card className="p-4 bg-red-100 dark:bg-red-900/20 border-red-200 dark:border-red-800">
                    <p>This content only displays on extra small screens (below sm breakpoint)</p>
                  </Card>
                </Responsive.Show>
                
                <Responsive.Range from="sm" to="md">
                  <Card className="p-4 bg-orange-100 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800">
                    <p>This content only displays on small to medium screens</p>
                  </Card>
                </Responsive.Range>
                
                <Responsive.For only={["lg", "xl"]}>
                  <Card className="p-4 bg-green-100 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                    <p>This content only displays on large and extra large screens</p>
                  </Card>
                </Responsive.For>
                
                <Responsive.Show breakpoint="xl" above={true}>
                  <Card className="p-4 bg-blue-100 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                    <p>This content displays on extra large screens and above</p>
                  </Card>
                </Responsive.Show>
              </div>
            </div>
            
            {/* Device-specific content */}
            <div className="space-y-6">
              <h3 className="text-xl font-medium">Device-Specific Content</h3>
              
              <div className="space-y-4">
                <Responsive.Device device="mobile">
                  <Card className="p-4 flex items-center gap-3 bg-pink-100 dark:bg-pink-900/20 border-pink-200 dark:border-pink-800">
                    <PhoneIcon className="h-10 w-10 text-pink-500" />
                    <div>
                      <h4 className="font-bold">Mobile View</h4>
                      <p>Content optimized for mobile devices</p>
                    </div>
                  </Card>
                </Responsive.Device>
                
                <Responsive.Device device="tablet">
                  <Card className="p-4 flex items-center gap-3 bg-purple-100 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                    <TabletIcon className="h-10 w-10 text-purple-500" />
                    <div>
                      <h4 className="font-bold">Tablet View</h4>
                      <p>Content optimized for tablet devices</p>
                    </div>
                  </Card>
                </Responsive.Device>
                
                <Responsive.Device device="laptop">
                  <Card className="p-4 flex items-center gap-3 bg-indigo-100 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800">
                    <LaptopIcon className="h-10 w-10 text-indigo-500" />
                    <div>
                      <h4 className="font-bold">Laptop View</h4>
                      <p>Content optimized for laptops</p>
                    </div>
                  </Card>
                </Responsive.Device>
                
                <Responsive.Device device="desktop">
                  <Card className="p-4 flex items-center gap-3 bg-cyan-100 dark:bg-cyan-900/20 border-cyan-200 dark:border-cyan-800">
                    <MonitorIcon className="h-10 w-10 text-cyan-500" />
                    <div>
                      <h4 className="font-bold">Desktop View</h4>
                      <p>Content optimized for desktop computers</p>
                    </div>
                  </Card>
                </Responsive.Device>
              </div>
            </div>
          </div>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Responsive Layout Direction</h2>
          
          <Flex 
            direction="column" 
            mdDirection="row" 
            gap={4} 
            className="border rounded-lg p-4"
          >
            <Card className="p-6 flex-1">
              <h3 className="font-bold mb-2">Panel 1</h3>
              <p className="text-muted-foreground">
                This layout is vertical on mobile and horizontal on larger screens.
              </p>
            </Card>
            <Card className="p-6 flex-1">
              <h3 className="font-bold mb-2">Panel 2</h3>
              <p className="text-muted-foreground">
                Resize your browser to see how the direction changes.
              </p>
            </Card>
            <Card className="p-6 flex-1">
              <h3 className="font-bold mb-2">Panel 3</h3>
              <p className="text-muted-foreground">
                Flex direction changes based on screen size.
              </p>
            </Card>
          </Flex>
        </section>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Mobile Navigation Example</h2>
          
          <Card className="p-6">
            <p className="mb-4">Try the mobile navigation menu:</p>
            <MobileNav 
              logo={<span className="font-bold text-xl">Demo App</span>}
              className="border p-2 inline-block"
            >
              <MobileNav.Item href="#home">Home</MobileNav.Item>
              <MobileNav.Item href="#features">Features</MobileNav.Item>
              <MobileNav.Item href="#pricing">Pricing</MobileNav.Item>
              <MobileNav.Group label="Resources" icon={<LaptopIcon className="h-4 w-4" />}>
                <MobileNav.Item href="#docs">Documentation</MobileNav.Item>
                <MobileNav.Item href="#tutorials">Tutorials</MobileNav.Item>
                <MobileNav.Item href="#guides">Guides</MobileNav.Item>
              </MobileNav.Group>
              <MobileNav.Item href="#contact">Contact</MobileNav.Item>
            </MobileNav>
          </Card>
        </section>
      </div>
      
      <ResponsiveDebugger position="bottom-right" />
    </Container>
  );
} 