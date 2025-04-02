"use client";

import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle,
  DialogTrigger 
} from "@/components/ui/dialog";
import { Flex } from "@/components/ui/flex";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Loader2 } from "lucide-react";

// Define the notification preferences schema
const notificationSchema = z.object({
  // Email notifications
  emailProjectUpdates: z.boolean().default(true),
  emailAnalysisComplete: z.boolean().default(true),
  emailWeeklyReports: z.boolean().default(true),
  emailSecurityAlerts: z.boolean().default(true),
  emailNewsletter: z.boolean().default(false),
  emailPromotions: z.boolean().default(false),
  
  // In-app notifications
  appProjectUpdates: z.boolean().default(true),
  appAnalysisComplete: z.boolean().default(true),
  appWeeklyReports: z.boolean().default(true),
  appSecurityAlerts: z.boolean().default(true),
  appTips: z.boolean().default(true),
  appAnnouncements: z.boolean().default(true),
});

type NotificationFormValues = z.infer<typeof notificationSchema>;

// Mock default values - would come from API in production
const defaultValues: NotificationFormValues = {
  // Email notifications
  emailProjectUpdates: true,
  emailAnalysisComplete: true,
  emailWeeklyReports: false,
  emailSecurityAlerts: true,
  emailNewsletter: false,
  emailPromotions: false,
  
  // In-app notifications
  appProjectUpdates: true,
  appAnalysisComplete: true,
  appWeeklyReports: true,
  appSecurityAlerts: true,
  appTips: true,
  appAnnouncements: false,
};

export function NotificationPreferences({ type = "email" }: { type?: "email" | "in-app" }) {
  const [open, setOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<string>(type === "email" ? "email" : "in-app");

  // Initialize form with react-hook-form and zod validation
  const form = useForm<NotificationFormValues>({
    resolver: zodResolver(notificationSchema),
    defaultValues,
  });

  // Handle form submission
  async function onSubmit(data: NotificationFormValues) {
    setIsSubmitting(true);
    
    try {
      // Simulate API call with timeout
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Success toast notification
      toast.success("Notification preferences updated!", {
        description: "Your notification settings have been saved.",
      });
      
      // Close dialog
      setOpen(false);
    } catch (error) {
      // Error toast notification
      toast.error("Failed to update notification preferences", {
        description: "There was an error saving your notification preferences. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  const buttonText = type === "email" ? "Manage Email Preferences" : "Manage In-App Notifications";
  const buttonVariant = type === "email" ? "default" : "outline";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant={buttonVariant as "default" | "outline"}>
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Notification Preferences</DialogTitle>
          <DialogDescription>
            Customize when and how you receive notifications
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="email">Email</TabsTrigger>
            <TabsTrigger value="in-app">In-App</TabsTrigger>
          </TabsList>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <TabsContent value="email" className="mt-4 space-y-4">
                <div className="text-sm text-muted-foreground mb-2">
                  Choose which email notifications you&apos;d like to receive
                </div>
                
                <FormField
                  control={form.control}
                  name="emailProjectUpdates"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Project Updates</FormLabel>
                        <FormDescription>
                          Receive emails about changes to your projects
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="emailAnalysisComplete"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Analysis Complete</FormLabel>
                        <FormDescription>
                          Get notified when your SEO analysis is complete
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="emailWeeklyReports"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Weekly Reports</FormLabel>
                        <FormDescription>
                          Receive weekly summary reports for your projects
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="emailSecurityAlerts"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Security Alerts</FormLabel>
                        <FormDescription>
                          Get important security notifications
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="emailNewsletter"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Newsletter</FormLabel>
                        <FormDescription>
                          Receive our monthly newsletter with SEO tips
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="emailPromotions"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Promotions</FormLabel>
                        <FormDescription>
                          Receive emails about special offers and upgrades
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </TabsContent>
              
              <TabsContent value="in-app" className="mt-4 space-y-4">
                <div className="text-sm text-muted-foreground mb-2">
                  Choose which in-app notifications you&apos;d like to receive
                </div>
                
                <FormField
                  control={form.control}
                  name="appProjectUpdates"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Project Updates</FormLabel>
                        <FormDescription>
                          Notifications about changes to your projects
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="appAnalysisComplete"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Analysis Complete</FormLabel>
                        <FormDescription>
                          Notifications when your SEO analysis is complete
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="appWeeklyReports"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Weekly Reports</FormLabel>
                        <FormDescription>
                          Weekly summary notifications for your projects
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="appSecurityAlerts"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Security Alerts</FormLabel>
                        <FormDescription>
                          Important security notifications
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="appTips"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>SEO Tips</FormLabel>
                        <FormDescription>
                          Helpful tips and suggestions for improving your SEO
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="appAnnouncements"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                      <div className="space-y-0.5">
                        <FormLabel>Announcements</FormLabel>
                        <FormDescription>
                          Updates about new features and improvements
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </TabsContent>
              
              <DialogFooter className="mt-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setOpen(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  {isSubmitting ? "Saving..." : "Save Preferences"}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
} 