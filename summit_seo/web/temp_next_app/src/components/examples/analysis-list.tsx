"use client";

import { useState } from "react";
import { useProjectAnalyses, useCreateAnalysis } from "@/lib/services";
import { Button } from "@/components/ui/button";
import { AnalysisStatus } from "@/types/api";

interface AnalysisListProps {
  projectId: string;
}

/**
 * Example analysis list component demonstrating React Query and API service usage
 */
export function AnalysisList({ projectId }: AnalysisListProps) {
  const [page, setPage] = useState(1);
  const pageSize = 5;
  const [statusFilter, setStatusFilter] = useState<AnalysisStatus[]>([]);
  
  // Query analyses with pagination and filtering
  const { 
    data: analysesData, 
    isLoading, 
    error 
  } = useProjectAnalyses(projectId, {
    page,
    page_size: pageSize,
    filter: statusFilter.length ? { status: statusFilter } : undefined,
  });
  
  // Mutation for creating a new analysis
  const createAnalysis = useCreateAnalysis(projectId);
  
  // Handle creating a new analysis
  const handleCreateAnalysis = () => {
    createAnalysis.mutate({
      analyzers: ["seo", "performance", "security", "accessibility"],
    });
  };
  
  // Handle pagination
  const handleNextPage = () => {
    if (analysesData?.pagination && analysesData.pagination.page < analysesData.pagination.pages) {
      setPage(page + 1);
    }
  };
  
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };
  
  // Handle status filter
  const toggleStatusFilter = (status: AnalysisStatus) => {
    setStatusFilter(prev => 
      prev.includes(status)
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
    setPage(1); // Reset to first page when filtering
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
  
  if (isLoading) {
    return <div className="p-4">Loading analyses...</div>;
  }
  
  if (error) {
    return <div className="p-4 text-red-500">Error: {String(error)}</div>;
  }
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Analyses</h2>
        <Button onClick={handleCreateAnalysis} disabled={createAnalysis.isPending}>
          {createAnalysis.isPending ? "Creating..." : "New Analysis"}
        </Button>
      </div>
      
      <div className="mb-4 flex flex-wrap gap-2">
        <span className="text-sm text-gray-600">Filter by status:</span>
        {Object.values(AnalysisStatus).map(status => (
          <button
            key={status}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              statusFilter.includes(status)
                ? "bg-primary text-primary-foreground"
                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
            }`}
            onClick={() => toggleStatusFilter(status)}
          >
            {status}
          </button>
        ))}
      </div>
      
      {!analysesData?.data?.length ? (
        <div className="p-4 text-center">No analyses found</div>
      ) : (
        <>
          <div className="space-y-4">
            {analysesData.data.map((analysis) => (
              <div
                key={analysis.id}
                className="p-4 border rounded shadow hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold">Analysis {analysis.id.split('-')[0]}</h3>
                    <div className="mt-1 flex items-center gap-2">
                      <StatusBadge status={analysis.status} />
                      <span className="text-sm text-gray-600">
                        Created: {new Date(analysis.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    {analysis.overall_score !== null && (
                      <div className="text-2xl font-bold">
                        {Math.round(analysis.overall_score)} / 100
                      </div>
                    )}
                    {analysis.status === AnalysisStatus.RUNNING && (
                      <div className="mt-1">
                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${analysis.progress}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          {analysis.progress}% complete
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mt-3 flex flex-wrap gap-1">
                  {analysis.analyzers.map((analyzer) => (
                    <span
                      key={analyzer}
                      className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs"
                    >
                      {analyzer}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Showing {analysesData.pagination?.page || 1} of {analysesData.pagination?.pages || 1} pages
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handlePrevPage} 
                disabled={page <= 1}
              >
                Previous
              </Button>
              <Button 
                variant="outline" 
                onClick={handleNextPage} 
                disabled={!analysesData?.pagination || analysesData.pagination.page >= analysesData.pagination.pages}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
} 