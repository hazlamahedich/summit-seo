"use client";

import { useState } from "react";
import { useAnalyses } from "@/lib/services";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { Grid } from "@/components/ui/grid";
import { Flex } from "@/components/ui/flex";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { MotionCard } from "@/components/ui/motion-card";
import Link from "next/link";
import { 
  Plus, 
  Search, 
  Filter, 
  RefreshCw, 
  Calendar, 
  TrendingUp, 
  BarChart2,
  Loader2
} from "lucide-react";
import ThemeSwitcher from "@/components/theme-switcher";
import { AnalysisStatus } from "@/types/api";
import { formatDistanceToNow } from "date-fns";

export default function AnalysesPage() {
  // State
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<AnalysisStatus | null>(null);
  const pageSize = 12;

  // Fetch analyses
  const { 
    data: analysesData, 
    isLoading, 
    error,
    refetch
  } = useAnalyses({
    page,
    page_size: pageSize,
    search: searchTerm || undefined,
    filter: statusFilter ? { status: statusFilter } : undefined
  });

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setPage(1);
  };

  // Handle status filter
  const handleStatusFilter = (status: AnalysisStatus | null) => {
    setStatusFilter(status);
    setPage(1);
  };

  // Status badge component
  const StatusBadge = ({ status }: { status: AnalysisStatus }) => {
    const colors = {
      [AnalysisStatus.PENDING]: "bg-yellow-100 text-yellow-800",
      [AnalysisStatus.RUNNING]: "bg-blue-100 text-blue-800",
      [AnalysisStatus.COMPLETED]: "bg-green-100 text-green-800",
      [AnalysisStatus.FAILED]: "bg-red-100 text-red-800",
      [AnalysisStatus.CANCELLED]: "bg-gray-100 text-gray-800",
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs ${colors[status]}`}>
        {status}
      </span>
    );
  };

  // Dashboard header with navigation
  const navigation = (
    <>
      <Button variant="ghost" asChild>
        <Link href="/dashboard">Dashboard</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/projects">Projects</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/analyses">Analyses</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/settings">Settings</Link>
      </Button>
    </>
  );

  // Dashboard logo
  const logo = (
    <Link href="/dashboard" className="flex items-center">
      <span className="font-bold text-xl">Summit SEO</span>
    </Link>
  );

  // Sidebar footer
  const sidebarFooter = (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-muted-foreground">Dark Mode</span>
        <ThemeSwitcher />
      </div>
      <Button size="sm" className="w-full" asChild>
        <Link href="/support">Get Support</Link>
      </Button>
    </div>
  );

  return (
    <DashboardLayout
      headerLogo={logo}
      navigation={navigation}
      sidebar={<DefaultDashboardSidebar logo={logo} footer={sidebarFooter} />}
      containerSize="xl"
      contentClassName="py-6"
    >
      <Section className="mb-6">
        <Flex justify="between" align="center" className="mb-4">
          <h1 className="text-3xl font-bold">Analyses</h1>
          <Button asChild>
            <Link href="/analyses/new">
              <Flex gap={2} align="center">
                <Plus className="h-4 w-4" />
                New Analysis
              </Flex>
            </Link>
          </Button>
        </Flex>
        
        <p className="text-muted-foreground mb-6">
          View and manage your website analyses
        </p>
        
        {/* Search and filters */}
        <Flex gap={4} className="mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search analyses..."
              className="pl-10"
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>
          <Button variant="outline" size="icon" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <div>
            <Button variant="outline" onClick={() => setStatusFilter(null)}>
              <Flex gap={2} align="center">
                <Filter className="h-4 w-4" />
                {statusFilter ? `Status: ${statusFilter}` : "All Statuses"}
              </Flex>
            </Button>
          </div>
        </Flex>
        
        {/* Status filter pills */}
        <Flex gap={2} className="mb-6">
          <Button 
            variant={statusFilter === null ? "default" : "outline"} 
            size="sm"
            onClick={() => handleStatusFilter(null)}
          >
            All
          </Button>
          {Object.values(AnalysisStatus).map(status => (
            <Button
              key={status}
              variant={statusFilter === status ? "default" : "outline"}
              size="sm"
              onClick={() => handleStatusFilter(status)}
            >
              {status}
            </Button>
          ))}
        </Flex>
        
        {isLoading ? (
          // Loading state
          <div className="py-12 text-center">
            <div className="inline-block animate-spin mr-2">
              <Loader2 className="h-6 w-6" />
            </div>
            <p>Loading analyses...</p>
          </div>
        ) : error ? (
          // Error state
          <div className="py-12 text-center text-red-500">
            <p>Error loading analyses. Please try again.</p>
            <Button variant="outline" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        ) : !analysesData?.data?.length ? (
          // Empty state
          <div className="py-12 text-center border rounded-lg">
            <h3 className="text-xl font-medium mb-2">No analyses found</h3>
            <p className="text-muted-foreground mb-4">
              {searchTerm 
                ? `No analyses match "${searchTerm}"`
                : "Get started by creating your first analysis"}
            </p>
            
            <Button asChild>
              <Link href="/analyses/new">
                <Flex gap={2} align="center">
                  <Plus className="h-4 w-4" />
                  Start New Analysis
                </Flex>
              </Link>
            </Button>
          </div>
        ) : (
          // Analyses grid
          <>
            <Grid
              cols={{ default: 1, sm: 2, lg: 3 }}
              gap={6}
              className="mb-8"
            >
              {analysesData.data.map((analysis) => {
                // Format the date
                const formattedDate = formatDistanceToNow(new Date(analysis.created_at), { addSuffix: true });
                
                return (
                  <MotionCard
                    key={analysis.id}
                    variant="hover-lift"
                    className="p-5"
                  >
                    <Flex direction="col" className="h-full">
                      <Flex justify="between" className="mb-2">
                        <StatusBadge status={analysis.status} />
                        <span className="text-sm text-muted-foreground">ID: {analysis.id.slice(0, 8)}</span>
                      </Flex>
                      
                      <h3 className="text-lg font-semibold mb-2">
                        Analysis for Project {analysis.project_id.slice(0, 8)}
                      </h3>
                      
                      <Flex align="center" gap={2} className="text-sm text-muted-foreground mb-3">
                        <Calendar className="h-4 w-4" />
                        <span>Created {formattedDate}</span>
                      </Flex>
                      
                      {analysis.status === AnalysisStatus.RUNNING && (
                        <div className="mb-3">
                          <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all"
                              style={{ width: `${analysis.progress}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1 text-right">
                            {analysis.progress}% complete
                          </div>
                        </div>
                      )}
                      
                      {analysis.overall_score !== null && (
                        <Flex align="center" gap={2} className="mb-3">
                          <TrendingUp className="h-4 w-4 text-primary" />
                          <span className="font-medium">
                            Score: {Math.round(analysis.overall_score)}/100
                          </span>
                        </Flex>
                      )}
                      
                      <Flex gap={2} className="mb-4 flex-wrap">
                        {analysis.analyzers.map((analyzer) => (
                          <Badge key={analyzer} variant="outline">
                            {analyzer}
                          </Badge>
                        ))}
                      </Flex>
                      
                      {/* Push the button to the bottom */}
                      <div className="mt-auto">
                        <Button asChild className="w-full">
                          <Link href={`/analyses/${analysis.id}`}>
                            <Flex gap={2} align="center" justify="center">
                              <BarChart2 className="h-4 w-4" />
                              <span>
                                {analysis.status === AnalysisStatus.COMPLETED ? 'View Results' : 'View Details'}
                              </span>
                            </Flex>
                          </Link>
                        </Button>
                      </div>
                    </Flex>
                  </MotionCard>
                );
              })}
            </Grid>
            
            {/* Pagination */}
            {analysesData.pagination && analysesData.pagination.pages > 1 && (
              <Flex justify="between" align="center" className="mt-6">
                <div className="text-sm text-muted-foreground">
                  Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, analysesData.pagination.total)} of {analysesData.pagination.total} analyses
                </div>
                <Flex gap={2}>
                  <Button
                    variant="outline"
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    disabled={page >= analysesData.pagination.pages}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </Flex>
              </Flex>
            )}
          </>
        )}
      </Section>
    </DashboardLayout>
  );
} 