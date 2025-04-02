"use client";

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { KeymapButton } from '@/components/ui/keymap-button';
import { SoundSettings } from '@/components/ui/sound-settings';
import { TourButton } from '@/components/onboarding/product-tour';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Info, Keyboard, Volume2, Layers, Monitor, Bell, User, Shield } from 'lucide-react';
import { useSoundEffectsContext } from '@/contexts/sound-effects-context';

export default function SettingsPage() {
  const { playClick } = useSoundEffectsContext();
  
  // Function to handle tab change with sound
  const handleTabChange = (value: string) => {
    playClick();
    // Additional tab change handling if needed
  };
  
  return (
    <div className="container py-10">
      <h1 className="text-3xl font-bold mb-2">Settings</h1>
      <p className="text-muted-foreground mb-8">
        Manage your application preferences and settings
      </p>
      
      <Tabs defaultValue="accessibility" onValueChange={handleTabChange}>
        <TabsList className="mb-8">
          <TabsTrigger value="accessibility">
            <Keyboard className="h-4 w-4 mr-2" />
            Accessibility
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Monitor className="h-4 w-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="account">
            <User className="h-4 w-4 mr-2" />
            Account
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="advanced">
            <Layers className="h-4 w-4 mr-2" />
            Advanced
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="accessibility" className="space-y-6">
          {/* Keyboard Shortcuts */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Keyboard Shortcuts</CardTitle>
                  <CardDescription>
                    Configure and view keyboard shortcuts for quick navigation
                  </CardDescription>
                </div>
                <KeymapButton size="sm" showTooltip={false} />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="keyboard-shortcuts">Enable keyboard shortcuts</Label>
                  <p className="text-sm text-muted-foreground">
                    Use keyboard shortcuts for faster navigation and actions
                  </p>
                </div>
                <Switch id="keyboard-shortcuts" defaultChecked />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>View all shortcuts</Label>
                  <p className="text-sm text-muted-foreground">
                    See a list of all available keyboard shortcuts
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={() => playClick()}>
                  <Keyboard className="h-4 w-4 mr-2" />
                  View Shortcuts
                </Button>
              </div>
            </CardContent>
          </Card>
          
          {/* Sound Effects */}
          <Card>
            <CardHeader>
              <CardTitle>Sound Effects</CardTitle>
              <CardDescription>
                Configure UI sound effects and feedback
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-0.5">
                  <Label>Sound settings</Label>
                  <p className="text-sm text-muted-foreground">
                    Adjust volume and toggle sound effects
                  </p>
                </div>
                <SoundSettings />
              </div>
            </CardContent>
          </Card>
          
          {/* Product Tour */}
          <Card>
            <CardHeader>
              <CardTitle>Product Tour</CardTitle>
              <CardDescription>
                Take a guided tour of the application features
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Start the product tour</Label>
                  <p className="text-sm text-muted-foreground">
                    Get a guided walkthrough of the application's key features
                  </p>
                </div>
                <TourButton />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>
                Customize how the application looks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Appearance settings coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>
                Configure how you receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Notification settings coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="account">
          <Card>
            <CardHeader>
              <CardTitle>Account Settings</CardTitle>
              <CardDescription>
                Manage your account information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Account settings coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Manage your account security
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Security settings coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="advanced">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>
                Configure advanced application settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Advanced settings coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 