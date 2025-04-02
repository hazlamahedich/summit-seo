'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '@/providers/auth-provider';
import { supabase } from '@/lib/supabase';

export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  size: 'small' | 'medium' | 'large';
  position: number;
  settings?: Record<string, any>;
  visible: boolean;
}

export interface UserPreferences {
  dashboardWidgets: DashboardWidget[];
  colorMode?: 'light' | 'dark' | 'system';
  notificationSettings?: Record<string, boolean>;
}

const DEFAULT_DASHBOARD_WIDGETS: DashboardWidget[] = [
  {
    id: 'summary-metrics',
    type: 'metrics-summary',
    title: 'Summary Metrics',
    size: 'large',
    position: 0,
    visible: true
  },
  {
    id: 'recent-projects',
    type: 'recent-projects',
    title: 'Recent Projects',
    size: 'medium',
    position: 1,
    visible: true
  },
  {
    id: 'recent-analyses',
    type: 'recent-analyses',
    title: 'Recent Analyses',
    size: 'medium',
    position: 2,
    visible: true
  },
  {
    id: 'seo-score-trends',
    type: 'line-chart',
    title: 'SEO Score Trends',
    size: 'medium',
    position: 3,
    visible: true,
    settings: {
      dataKey: 'seo-scores',
      timeRange: 'month'
    }
  },
  {
    id: 'critical-issues',
    type: 'issues-summary',
    title: 'Critical Issues',
    size: 'small',
    position: 4,
    visible: true,
    settings: {
      severity: 'critical'
    }
  }
];

const DEFAULT_PREFERENCES: UserPreferences = {
  dashboardWidgets: DEFAULT_DASHBOARD_WIDGETS,
  colorMode: 'system',
  notificationSettings: {
    email: true,
    browser: true,
    critical: true,
    weekly: true
  }
};

interface UserPreferencesContextType {
  preferences: UserPreferences;
  isLoading: boolean;
  updatePreferences: (newPreferences: Partial<UserPreferences>) => Promise<void>;
  updateWidgetPosition: (widgetId: string, newPosition: number) => Promise<void>;
  updateWidgetVisibility: (widgetId: string, visible: boolean) => Promise<void>;
  updateWidgetSize: (widgetId: string, size: 'small' | 'medium' | 'large') => Promise<void>;
  updateWidgetSettings: (widgetId: string, settings: Record<string, any>) => Promise<void>;
  resetWidgets: () => Promise<void>;
  addWidget: (widget: Omit<DashboardWidget, 'position'>) => Promise<void>;
  removeWidget: (widgetId: string) => Promise<void>;
}

const UserPreferencesContext = createContext<UserPreferencesContextType | undefined>(undefined);

export function useUserPreferences() {
  const context = useContext(UserPreferencesContext);
  if (context === undefined) {
    throw new Error('useUserPreferences must be used within a UserPreferencesProvider');
  }
  return context;
}

export function UserPreferencesProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [isLoading, setIsLoading] = useState(true);

  // Load user preferences from Supabase on auth state change
  useEffect(() => {
    const loadUserPreferences = async () => {
      if (!user) {
        setPreferences(DEFAULT_PREFERENCES);
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        
        // Query the settings table for user preferences
        const { data, error } = await supabase
          .from('settings')
          .select('*')
          .eq('scope', 'user')
          .eq('scope_id', user.id)
          .eq('key', 'user_preferences')
          .single();

        if (error && error.code !== 'PGRST116') { // PGRST116 is "not found"
          console.error('Error fetching user preferences:', error);
          setPreferences(DEFAULT_PREFERENCES);
          return;
        }

        // If preferences found, parse the value
        if (data) {
          try {
            const parsedPreferences = JSON.parse(data.value);
            // Merge with defaults to ensure all expected fields exist
            setPreferences({
              ...DEFAULT_PREFERENCES,
              ...parsedPreferences
            });
          } catch (e) {
            console.error('Error parsing user preferences:', e);
            setPreferences(DEFAULT_PREFERENCES);
          }
        } else {
          // No preferences found, use defaults and save them
          await savePreferences(DEFAULT_PREFERENCES);
          setPreferences(DEFAULT_PREFERENCES);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadUserPreferences();
  }, [user]);

  // Save preferences to Supabase
  const savePreferences = async (newPreferences: UserPreferences) => {
    if (!user) return;

    try {
      const { error } = await supabase
        .from('settings')
        .upsert({
          key: 'user_preferences',
          value: JSON.stringify(newPreferences),
          scope: 'user',
          scope_id: user.id,
          description: 'User preferences including dashboard widget configuration'
        }, { onConflict: 'key,scope,scope_id' });

      if (error) {
        console.error('Error saving user preferences:', error);
        throw error;
      }
    } catch (error) {
      console.error('Unexpected error saving preferences:', error);
      throw error;
    }
  };

  // Update preferences
  const updatePreferences = async (newPreferences: Partial<UserPreferences>) => {
    const updatedPreferences = {
      ...preferences,
      ...newPreferences
    };
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Update widget position
  const updateWidgetPosition = async (widgetId: string, newPosition: number) => {
    const updatedWidgets = [...preferences.dashboardWidgets];
    const widgetIndex = updatedWidgets.findIndex(w => w.id === widgetId);
    
    if (widgetIndex === -1) return;
    
    updatedWidgets[widgetIndex] = {
      ...updatedWidgets[widgetIndex],
      position: newPosition
    };
    
    // Sort widgets by position
    updatedWidgets.sort((a, b) => a.position - b.position);
    
    // Update preferences
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Update widget visibility
  const updateWidgetVisibility = async (widgetId: string, visible: boolean) => {
    const updatedWidgets = preferences.dashboardWidgets.map(widget => 
      widget.id === widgetId ? { ...widget, visible } : widget
    );
    
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Update widget size
  const updateWidgetSize = async (widgetId: string, size: 'small' | 'medium' | 'large') => {
    const updatedWidgets = preferences.dashboardWidgets.map(widget => 
      widget.id === widgetId ? { ...widget, size } : widget
    );
    
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Update widget settings
  const updateWidgetSettings = async (widgetId: string, settings: Record<string, any>) => {
    const updatedWidgets = preferences.dashboardWidgets.map(widget => 
      widget.id === widgetId ? { 
        ...widget, 
        settings: { ...(widget.settings || {}), ...settings } 
      } : widget
    );
    
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Reset widgets to default
  const resetWidgets = async () => {
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: DEFAULT_DASHBOARD_WIDGETS
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Add a new widget
  const addWidget = async (widget: Omit<DashboardWidget, 'position'>) => {
    // Find the highest position
    const highestPosition = preferences.dashboardWidgets.reduce(
      (max, w) => Math.max(max, w.position), -1
    );
    
    const newWidget: DashboardWidget = {
      ...widget as any,
      position: highestPosition + 1
    };
    
    const updatedWidgets = [...preferences.dashboardWidgets, newWidget];
    
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  // Remove a widget
  const removeWidget = async (widgetId: string) => {
    const updatedWidgets = preferences.dashboardWidgets.filter(widget => widget.id !== widgetId);
    
    const updatedPreferences = {
      ...preferences,
      dashboardWidgets: updatedWidgets
    };
    
    setPreferences(updatedPreferences);
    await savePreferences(updatedPreferences);
  };

  const value = {
    preferences,
    isLoading,
    updatePreferences,
    updateWidgetPosition,
    updateWidgetVisibility,
    updateWidgetSize,
    updateWidgetSettings,
    resetWidgets,
    addWidget,
    removeWidget
  };

  return (
    <UserPreferencesContext.Provider value={value}>
      {children}
    </UserPreferencesContext.Provider>
  );
} 