"use client";

import React, { useState, useEffect } from "react";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Flex } from "@/components/ui/flex";
import { Grid } from "@/components/ui/grid";
import { Section } from "@/components/ui/section";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { Loader2, ServerCrash, BarChart2, Users, Settings, RefreshCw } from "lucide-react";
import { toast } from "sonner";

// API connection utilities
import { apiClient } from "@/lib/api";

// Import admin components
import { UserManagement } from "@/components/admin/user-management";
import { SystemConfig } from "@/components/admin/system-config";

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("system");
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [serviceStatus, setServiceStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchSystemData = async () => {
    try {
      setIsRefreshing(true);
      const [infoResponse, statusResponse] = await Promise.all([
        apiClient.get("/system/info"),
        apiClient.get("/system/status"),
      ]);

      if (infoResponse.data && infoResponse.data.status === "success") {
        setSystemInfo(infoResponse.data.data);
      }

      if (statusResponse.data && statusResponse.data.status === "success") {
        setServiceStatus(statusResponse.data.data);
      }
    } catch (error) {
      console.error("Failed to fetch system data:", error);
      toast.error("Failed to load system information");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSystemData();
  }, []);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatUptime = (uptime: number) => {
    const days = Math.floor(uptime / 86400);
    const hours = Math.floor((uptime % 86400) / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  // Create sidebar navigation and logo
  const logo = (
    <div className="flex items-center gap-2 px-2 py-4">
      <ServerCrash className="h-6 w-6 text-primary" />
      <span className="font-bold text-xl">Admin</span>
    </div>
  );

  const handleRefresh = () => {
    fetchSystemData();
  };

  const handleRestartService = async () => {
    try {
      setIsRefreshing(true);
      const response = await apiClient.post("/system/restart");
      
      if (response.data && response.data.status === "success") {
        toast.success("Service restart requested successfully");
      }
    } catch (error) {
      console.error("Failed to restart service:", error);
      toast.error("Failed to restart service");
    } finally {
      setIsRefreshing(false);
    }
  };

  const renderSystemInfoContent = () => {
    if (isLoading) {
      return (
        <Flex justify="center" align="center" className="min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="ml-2">Loading system information...</p>
        </Flex>
      );
    }

    if (!systemInfo) {
      return (
        <Card className="p-6">
          <p className="text-center text-muted-foreground">
            System information is not available
          </p>
        </Card>
      );
    }

    return (
      <>
        <Grid cols={{ default: 1, md: 2 }} gap={6}>
          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">System Overview</h3>
            <Flex direction="col" gap={2}>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Platform</span>
                <span>{systemInfo.system.platform} {systemInfo.system.platform_release}</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Version</span>
                <span>{systemInfo.app.version} ({systemInfo.app.environment})</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Host</span>
                <span>{systemInfo.system.hostname}</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Architecture</span>
                <span>{systemInfo.system.architecture}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Python Version</span>
                <span>{systemInfo.system.python_version}</span>
              </div>
            </Flex>
          </Card>

          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">Resource Usage</h3>
            <Flex direction="col" gap={2}>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">CPU Cores</span>
                <span>{systemInfo.cpu.cores_physical} physical / {systemInfo.cpu.cores_logical} logical</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">CPU Usage</span>
                <span className={systemInfo.cpu.percent_used > 80 ? "text-destructive" : ""}>{systemInfo.cpu.percent_used}%</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Memory</span>
                <span className={systemInfo.memory.percent_used > 80 ? "text-destructive" : ""}>
                  {formatBytes(systemInfo.memory.used)} / {formatBytes(systemInfo.memory.total)} ({systemInfo.memory.percent_used}%)
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Disk</span>
                <span className={systemInfo.disk.percent_used > 80 ? "text-destructive" : ""}>
                  {formatBytes(systemInfo.disk.used)} / {formatBytes(systemInfo.disk.total)} ({systemInfo.disk.percent_used}%)
                </span>
              </div>
            </Flex>
          </Card>
        </Grid>

        <Card className="p-4 mt-6">
          <h3 className="text-lg font-semibold mb-3">Service Status</h3>
          {serviceStatus ? (
            <Flex direction="col" gap={2}>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Status</span>
                <span className={serviceStatus.status === "operational" ? "text-green-500" : "text-destructive"}>
                  {serviceStatus.status.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Uptime</span>
                <span>{formatUptime(serviceStatus.uptime)}</span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Load Average</span>
                <span>
                  {serviceStatus.load["1m"].toFixed(2)} (1m), {serviceStatus.load["5m"].toFixed(2)} (5m), {serviceStatus.load["15m"].toFixed(2)} (15m)
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Memory Usage</span>
                <span className={serviceStatus.memory.used_percent > 80 ? "text-destructive" : ""}>
                  {serviceStatus.memory.used_percent}%
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Last Updated</span>
                <span>{new Date(serviceStatus.timestamp).toLocaleString()}</span>
              </div>
            </Flex>
          ) : (
            <p className="text-center text-muted-foreground">Service status is not available</p>
          )}
        </Card>

        <Flex justify="end" className="mt-6">
          <Button
            onClick={handleRestartService}
            variant="destructive"
            disabled={isRefreshing}
            className="mr-2"
          >
            {isRefreshing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
            Restart Service
          </Button>
          <Button
            onClick={handleRefresh}
            variant="outline"
            disabled={isRefreshing}
          >
            {isRefreshing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
            Refresh
          </Button>
        </Flex>
      </>
    );
  };

  return (
    <DashboardLayout
      headerLogo={logo}
      sidebar={
        <DefaultDashboardSidebar
          logo={logo}
          className="admin-sidebar"
        />
      }
      containerSize="xl"
      contentClassName="py-6"
    >
      <Section className="mb-6">
        <h1 className="text-3xl font-bold mb-2">System Administration</h1>
        <p className="text-muted-foreground">
          Manage system settings, users, and monitor performance
        </p>
      </Section>

      <Tabs defaultValue="system" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="system" className="flex items-center gap-1">
            <ServerCrash className="h-4 w-4" />
            <span>System</span>
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>Users</span>
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-1">
            <Settings className="h-4 w-4" />
            <span>Configuration</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-1">
            <BarChart2 className="h-4 w-4" />
            <span>Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="system">
          {renderSystemInfoContent()}
        </TabsContent>

        <TabsContent value="users">
          <UserManagement />
        </TabsContent>

        <TabsContent value="settings">
          <SystemConfig />
        </TabsContent>

        <TabsContent value="analytics">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">System Analytics</h3>
            <p>System analytics will be implemented in the next phase.</p>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
} 