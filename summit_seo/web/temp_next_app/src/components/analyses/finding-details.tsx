import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SeverityLevel, Finding } from "@/types/api";
import { AnimatedContainer } from "@/components/ui/animated-container";

interface FindingDetailsProps {
  finding: Finding;
  index: number;
}

const severityColors = {
  [SeverityLevel.CRITICAL]: {
    bg: "bg-red-50 dark:bg-red-950/20",
    border: "border-red-200 dark:border-red-900/50",
    text: "text-red-700 dark:text-red-400",
    badge: "bg-red-500 hover:bg-red-600"
  },
  [SeverityLevel.HIGH]: {
    bg: "bg-orange-50 dark:bg-orange-950/20",
    border: "border-orange-200 dark:border-orange-900/50",
    text: "text-orange-700 dark:text-orange-400",
    badge: "bg-orange-500 hover:bg-orange-600"
  },
  [SeverityLevel.MEDIUM]: {
    bg: "bg-amber-50 dark:bg-amber-950/20",
    border: "border-amber-200 dark:border-amber-900/50",
    text: "text-amber-700 dark:text-amber-400",
    badge: "bg-amber-500 hover:bg-amber-600"
  },
  [SeverityLevel.LOW]: {
    bg: "bg-blue-50 dark:bg-blue-950/20",
    border: "border-blue-200 dark:border-blue-900/50",
    text: "text-blue-700 dark:text-blue-400",
    badge: "bg-blue-500 hover:bg-blue-600"
  },
  [SeverityLevel.INFO]: {
    bg: "bg-gray-50 dark:bg-gray-900/20",
    border: "border-gray-200 dark:border-gray-800/50",
    text: "text-gray-700 dark:text-gray-400",
    badge: "bg-gray-500 hover:bg-gray-600"
  }
};

export function FindingDetails({ finding, index }: FindingDetailsProps) {
  const [expanded, setExpanded] = useState(false);
  const colors = severityColors[finding.severity];
  
  return (
    <AnimatedContainer delay={index * 0.05}>
      <Card 
        className={`p-4 border ${colors.border} ${colors.bg} cursor-pointer transition-all duration-200 ${expanded ? 'shadow-md' : ''}`}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <Badge className={`${colors.badge}`}>
                {finding.severity.toUpperCase()}
              </Badge>
              <span className={`font-medium ${colors.text}`}>{finding.message}</span>
            </div>
            
            {expanded && (
              <div className="mt-4 space-y-3 text-sm">
                {finding.description && (
                  <div>
                    <h4 className="font-semibold mb-1">Description</h4>
                    <p className="text-muted-foreground">{finding.description}</p>
                  </div>
                )}
                
                {finding.location && (
                  <div>
                    <h4 className="font-semibold mb-1">Location</h4>
                    <code className="px-2 py-1 bg-muted rounded text-xs">{finding.location}</code>
                  </div>
                )}
                
                {finding.details && Object.keys(finding.details).length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-1">Details</h4>
                    <pre className="px-2 py-1 bg-muted rounded text-xs overflow-x-auto">
                      {JSON.stringify(finding.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="text-xs text-muted-foreground whitespace-nowrap ml-4">
            {finding.category}
            {finding.subcategory && ` › ${finding.subcategory}`}
          </div>
        </div>
      </Card>
    </AnimatedContainer>
  );
} 