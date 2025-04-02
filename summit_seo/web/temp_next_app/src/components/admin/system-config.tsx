"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Flex } from "@/components/ui/flex";
import { Grid } from "@/components/ui/grid";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Loader2, RefreshCw, Edit, Save, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface ConfigSetting {
  key: string;
  value: any;
  description?: string;
  type?: string;
  category?: string;
}

export function SystemConfig() {
  const [settings, setSettings] = useState<ConfigSetting[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedSetting, setSelectedSetting] = useState<ConfigSetting | null>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editValue, setEditValue] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      
      const response = await apiClient.get<{data: Record<string, any>}>('/system/config');
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (response.data && response.data.data) {
        // Convert config object to array of settings
        const configData = response.data.data;
        const settingsArray: ConfigSetting[] = [];
        
        // Group by category if available
        const categorySet = new Set<string>();
        
        for (const key in configData) {
          const value = configData[key];
          const category = key.split('.')[0] || 'general';
          categorySet.add(category);
          
          settingsArray.push({
            key,
            value,
            category,
            type: typeof value,
            description: '' // Description would come from backend in a real implementation
          });
        }
        
        setSettings(settingsArray);
        setCategories(Array.from(categorySet));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch system configuration');
      console.error('Error fetching system config:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleEditSetting = async () => {
    if (!selectedSetting) return;
    
    try {
      let parsedValue;
      // Try to parse the value based on its original type
      switch(selectedSetting.type) {
        case 'number':
          parsedValue = Number(editValue);
          break;
        case 'boolean':
          parsedValue = editValue.toLowerCase() === 'true';
          break;
        case 'object':
          parsedValue = JSON.parse(editValue);
          break;
        default:
          parsedValue = editValue;
      }
      
      // In a real implementation, this would be an API call to update the setting
      toast.success(`Setting ${selectedSetting.key} updated successfully`);
      setShowEditDialog(false);
      
      // For now, we'll just simulate the update locally
      setSettings(settings.map(s => 
        s.key === selectedSetting.key ? { ...s, value: parsedValue } : s
      ));
    } catch (err) {
      toast.error(`Failed to update setting: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleRefresh = () => {
    fetchSettings();
  };

  const formatValue = (value: any, type: string = typeof value): string => {
    if (value === null || value === undefined) {
      return 'null';
    }
    if (type === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const getValueDisplay = (value: any, type: string = typeof value): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-muted-foreground">null</span>;
    }
    
    if (type === 'boolean') {
      return (
        <span className={value ? 'text-green-500' : 'text-red-500'}>
          {String(value)}
        </span>
      );
    }
    
    if (type === 'object') {
      // For objects, show summarized version
      if (Array.isArray(value)) {
        return <span>[{value.length} items]</span>;
      }
      return <span>{"{"}{Object.keys(value).length} properties{"}"}</span>;
    }
    
    return String(value);
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" className="min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="ml-2">Loading system configuration...</p>
      </Flex>
    );
  }

  return (
    <div>
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Flex justify="between" align="center" className="mb-4">
        <h3 className="text-xl font-semibold">System Configuration</h3>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isRefreshing}>
          {isRefreshing ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          Refresh
        </Button>
      </Flex>

      {categories.length === 0 ? (
        <Card className="p-6">
          <p className="text-center text-muted-foreground">No configuration settings found</p>
        </Card>
      ) : (
        categories.map((category) => (
          <Card key={category} className="p-4 mb-4">
            <h3 className="text-lg font-semibold mb-3 capitalize">{category}</h3>
            <div className="overflow-x-auto">
              <table className="w-full table-auto border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-2 text-left">Setting Key</th>
                    <th className="px-4 py-2 text-left">Value</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Description</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {settings
                    .filter(setting => setting.category === category)
                    .map((setting) => (
                      <tr key={setting.key} className="border-b hover:bg-muted/50">
                        <td className="px-4 py-3 font-medium">{setting.key}</td>
                        <td className="px-4 py-3">
                          <div className="max-w-xs truncate">
                            {getValueDisplay(setting.value, setting.type)}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-muted-foreground">{setting.type}</span>
                        </td>
                        <td className="px-4 py-3">
                          {setting.description || <span className="text-muted-foreground">-</span>}
                        </td>
                        <td className="px-4 py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => {
                              setSelectedSetting(setting);
                              setEditValue(formatValue(setting.value, setting.type));
                              setShowEditDialog(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </Card>
        ))
      )}

      {/* Edit Setting Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Configuration Setting</DialogTitle>
            <DialogDescription>
              {selectedSetting?.key && (
                <>Update the value for <span className="font-mono">{selectedSetting.key}</span></>
              )}
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4">
            {selectedSetting && (
              <>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-1">
                    Value ({selectedSetting.type})
                  </label>
                  {selectedSetting.type === 'object' ? (
                    <textarea
                      className="w-full h-40 p-2 border rounded-md font-mono text-sm"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                    />
                  ) : (
                    <input
                      type={selectedSetting.type === 'number' ? 'number' : 'text'}
                      className="w-full p-2 border rounded-md"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                    />
                  )}
                  <p className="text-sm text-muted-foreground mt-1">
                    {selectedSetting.description}
                  </p>
                </div>
              </>
            )}
          </div>
          
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                if (selectedSetting) {
                  setEditValue(formatValue(selectedSetting.value));
                }
              }}
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditSetting}>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 