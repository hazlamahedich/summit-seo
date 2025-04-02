"use client";

import React, { useState } from "react";
import { MobileAppShell } from "@/components/ui/mobile-app-shell";
import { SwipeContainer } from "@/components/ui/swipe-container";
import { SwipeCarousel } from "@/components/ui/swipe-carousel";
import { ResponsiveImage } from "@/components/ui/responsive-image";
import { BottomSheet } from "@/components/ui/bottom-sheet";
import { OfflineStatus } from "@/components/ui/offline-status";
import { PWAInstallPrompt } from "@/components/ui/pwa-install-prompt";
import { Button } from "@/components/ui/button";
import { useOfflineManager, useOnlineStatus } from "@/lib/offline-manager";
import { hapticFeedback } from "@/lib/haptics";
import { usePWA } from "@/hooks/usePWA";
import { 
  Menu,
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  Smartphone,
  Wifi,
  WifiOff,
  Layers,
  MoveHorizontal,
  ArrowUp,
  Download
} from "lucide-react";

/**
 * Example page showcasing mobile optimization components
 */
export default function MobileExamplePage() {
  const [bottomSheetOpen, setBottomSheetOpen] = useState(false);
  const [activeDemo, setActiveDemo] = useState<string | null>(null);
  const isOnline = useOnlineStatus();
  const { storeData, getData, queueRequest, pendingCount } = useOfflineManager();
  const { isInstallable, isInstalled, showInstallPrompt } = usePWA();
  
  // Demo refresh handler
  const handleRefresh = async () => {
    hapticFeedback("selection");
    console.log("Refreshing data...");
    
    // Simulate API request
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    return Promise.resolve();
  };
  
  // Mock offline data storage
  const handleStoreOfflineData = () => {
    hapticFeedback("light");
    storeData("demo-data", { timestamp: Date.now(), value: "Example data" });
    alert("Data stored offline!");
  };
  
  // Mock offline request queueing
  const handleQueueRequest = async () => {
    hapticFeedback("medium");
    await queueRequest({
      url: "/api/example",
      method: "POST",
      body: { action: "example" },
      maxRetries: 3,
      priority: 5
    });
    alert("Request queued for when online!");
  };
  
  // Handle PWA install
  const handleInstall = async () => {
    hapticFeedback("medium");
    const result = await showInstallPrompt();
    if (result === "accepted") {
      alert("Thanks for installing our app!");
    }
  };
  
  // Example header component
  const header = (
    <div className="flex items-center justify-between p-4 border-b">
      <div className="flex items-center">
        <Menu className="h-5 w-5 mr-3" />
        <h1 className="text-lg font-medium">Mobile Components Demo</h1>
      </div>
      <Button variant="ghost" size="icon" onClick={() => hapticFeedback("selection")}>
        <RefreshCw className="h-4 w-4" />
      </Button>
    </div>
  );
  
  // Demo card component
  const DemoCard = ({ title, icon, onClick }: { title: string, icon: React.ReactNode, onClick: () => void }) => (
    <Button 
      variant="outline" 
      className="h-auto p-4 flex flex-col items-center justify-center gap-2 w-full"
      onClick={() => {
        hapticFeedback("light");
        onClick();
      }}
    >
      {icon}
      <span>{title}</span>
    </Button>
  );
  
  // Render active demo or cards
  const renderContent = () => {
    if (activeDemo === "carousel") {
      return (
        <div className="p-4 space-y-4">
          <div className="flex justify-between items-center mb-6">
            <Button variant="ghost" onClick={() => setActiveDemo(null)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <h2 className="text-lg font-medium">Swipe Carousel</h2>
          </div>
          
          <SwipeCarousel 
            showArrows 
            showDots 
            className="h-72 mb-4 overflow-hidden rounded-lg"
          >
            {[1, 2, 3, 4, 5].map((i) => (
              <div 
                key={i} 
                className="h-full flex items-center justify-center bg-primary-100 dark:bg-primary-900"
              >
                <h3 className="text-2xl font-bold">Slide {i}</h3>
              </div>
            ))}
          </SwipeCarousel>
          
          <div className="p-4 bg-muted/30 rounded-lg">
            <h3 className="font-medium mb-2">Features:</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              <li>Touch swipe gestures</li>
              <li>Pagination indicators</li>
              <li>Navigation arrows</li>
              <li>Auto-play capability</li>
              <li>Customizable width and spacing</li>
            </ul>
          </div>
        </div>
      );
    }
    
    if (activeDemo === "swipe") {
      return (
        <div className="p-4 space-y-4">
          <div className="flex justify-between items-center mb-6">
            <Button variant="ghost" onClick={() => setActiveDemo(null)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <h2 className="text-lg font-medium">Swipe Navigation</h2>
          </div>
          
          <SwipeContainer
            onSwipeLeft={() => {
              hapticFeedback("light");
              alert("Swiped Left!");
            }}
            onSwipeRight={() => {
              hapticFeedback("light");
              alert("Swiped Right!");
            }}
            className="h-72 mb-4 overflow-hidden rounded-lg bg-muted/30 flex items-center justify-center"
            showSwipeHint
          >
            <div className="text-center p-4">
              <MoveHorizontal className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <h3 className="text-lg font-medium mb-1">Swipe Left or Right</h3>
              <p className="text-sm">Look for the swipe indicators on the sides</p>
            </div>
          </SwipeContainer>
          
          <div className="p-4 bg-muted/30 rounded-lg">
            <h3 className="font-medium mb-2">Features:</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              <li>Visual swipe indicators</li>
              <li>Haptic feedback on swipe</li>
              <li>Customizable swipe distance</li>
              <li>Multi-directional swipes (left, right, up, down)</li>
              <li>Mobile-only or all-device support</li>
            </ul>
          </div>
        </div>
      );
    }
    
    if (activeDemo === "offline") {
      return (
        <div className="p-4 space-y-4">
          <div className="flex justify-between items-center mb-6">
            <Button variant="ghost" onClick={() => setActiveDemo(null)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <h2 className="text-lg font-medium">Offline Capabilities</h2>
          </div>
          
          <div className="rounded-lg overflow-hidden mb-4">
            <div className="p-4 bg-primary-100 dark:bg-primary-900 flex items-center justify-between">
              <div className="flex items-center">
                {isOnline ? (
                  <Wifi className="h-5 w-5 mr-2 text-green-500" />
                ) : (
                  <WifiOff className="h-5 w-5 mr-2 text-red-500" />
                )}
                <span>Status: {isOnline ? 'Online' : 'Offline'}</span>
              </div>
              <span className="text-sm opacity-70">
                {pendingCount} pending requests
              </span>
            </div>
            
            <div className="p-6 border-x border-b rounded-b-lg space-y-3">
              <Button 
                variant="outline" 
                className="w-full"
                onClick={handleStoreOfflineData}
              >
                Store Offline Data
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full"
                onClick={handleQueueRequest}
              >
                Queue API Request
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => {
                  hapticFeedback("light");
                  const data = getData("demo-data");
                  alert(data ? `Retrieved data: ${JSON.stringify(data)}` : "No data found");
                }}
              >
                Retrieve Offline Data
              </Button>
            </div>
          </div>
          
          <div className="p-4 bg-muted/30 rounded-lg">
            <h3 className="font-medium mb-2">Features:</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              <li>Automatic online/offline detection</li>
              <li>Request queueing when offline</li>
              <li>Prioritized request processing</li>
              <li>Local data storage with TTL</li>
              <li>Automatic retry with backoff</li>
            </ul>
          </div>
        </div>
      );
    }
    
    if (activeDemo === "pwa") {
      return (
        <div className="p-4 space-y-4">
          <div className="flex justify-between items-center mb-6">
            <Button variant="ghost" onClick={() => setActiveDemo(null)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <h2 className="text-lg font-medium">PWA Installation</h2>
          </div>
          
          <div className="rounded-lg overflow-hidden mb-4 bg-primary-100 dark:bg-primary-900 p-6 text-center">
            <Download className="h-16 w-16 mx-auto mb-4 opacity-70" />
            <h3 className="text-xl font-medium mb-2">Install as App</h3>
            <p className="mb-6 text-sm opacity-80">
              Install Summit SEO as a standalone app on your device for a better experience.
            </p>
            
            <Button 
              disabled={!isInstallable || isInstalled}
              onClick={handleInstall}
              className="mx-auto"
            >
              {isInstalled ? "App Installed" : isInstallable ? "Install Now" : "Not Available"}
            </Button>
          </div>
          
          <div className="p-4 bg-muted/30 rounded-lg">
            <h3 className="font-medium mb-2">Features:</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              <li>App-like experience with no browser UI</li>
              <li>Home screen installation</li>
              <li>Offline access to cached resources</li>
              <li>Fast loading with service worker</li>
              <li>Background sync for offline operations</li>
              <li>Push notifications (if configured)</li>
            </ul>
          </div>
        </div>
      );
    }
    
    // Default view - component cards
    return (
      <div className="p-4 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <DemoCard 
            title="Swipe Carousel" 
            icon={<Layers className="h-10 w-10 opacity-70" />}
            onClick={() => setActiveDemo("carousel")}
          />
          
          <DemoCard 
            title="Swipe Navigation" 
            icon={<MoveHorizontal className="h-10 w-10 opacity-70" />}
            onClick={() => setActiveDemo("swipe")}
          />
          
          <DemoCard 
            title="Bottom Sheet" 
            icon={<ArrowUp className="h-10 w-10 opacity-70" />}
            onClick={() => setBottomSheetOpen(true)}
          />
          
          <DemoCard 
            title="Offline Features" 
            icon={<Wifi className="h-10 w-10 opacity-70" />}
            onClick={() => setActiveDemo("offline")}
          />
          
          <DemoCard 
            title="PWA Installation" 
            icon={<Download className="h-10 w-10 opacity-70" />}
            onClick={() => setActiveDemo("pwa")}
          />
        </div>
        
        <div className="mt-8 p-4 bg-muted/30 rounded-lg">
          <h3 className="font-medium mb-2">Pull to Refresh</h3>
          <p className="text-sm">Pull down from the top of the screen to trigger a refresh</p>
        </div>
        
        <div className="fixed bottom-4 left-0 right-0 flex justify-center">
          <Button 
            onClick={() => {
              hapticFeedback("medium");
              setBottomSheetOpen(true);
            }}
            className="shadow-lg"
          >
            Open Bottom Sheet
          </Button>
        </div>
      </div>
    );
  };
  
  return (
    <>
      <MobileAppShell
        header={header}
        enablePullToRefresh
        onRefresh={handleRefresh}
        showOfflineIndicator
        enableSwipeNavigation
        navRoutes={{
          back: "/example-mobile-page",
          forward: "/example-mobile-page"
        }}
      >
        {renderContent()}
      </MobileAppShell>
      
      <BottomSheet
        isOpen={bottomSheetOpen}
        onClose={() => setBottomSheetOpen(false)}
        showHandle
        height="50vh"
        snapPoints={["25vh", "50vh", "75vh"]}
      >
        <div className="p-4">
          <h2 className="text-lg font-medium mb-4">Bottom Sheet</h2>
          <p className="mb-4">This is a bottom sheet component with:</p>
          <ul className="list-disc pl-5 space-y-1 mb-6">
            <li>Drag to dismiss functionality</li>
            <li>Multiple snap points (try dragging)</li>
            <li>Swipe down to close</li>
            <li>Handle for easy dragging</li>
            <li>Responsive design for all screen sizes</li>
          </ul>
          
          <Button 
            variant="outline" 
            className="w-full"
            onClick={() => {
              hapticFeedback("medium");
              setBottomSheetOpen(false);
            }}
          >
            Close Sheet
          </Button>
        </div>
      </BottomSheet>
      
      {/* PWA Install Prompt */}
      <PWAInstallPrompt position="bottom" />
    </>
  );
} 