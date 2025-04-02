import { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Finding, SeverityLevel } from "@/types/api";
import { FindingDetails } from "./finding-details";
import { AnimatedContainer } from "@/components/ui/animated-container";
import { Input } from "@/components/ui/input";

interface FindingsListProps {
  findings: Finding[];
  title?: string;
}

type FilterOption = "all" | SeverityLevel;

export function FindingsList({ findings, title = "Findings" }: FindingsListProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterBySeverity, setFilterBySeverity] = useState<FilterOption>("all");
  
  const filteredFindings = useMemo(() => {
    return findings.filter(finding => {
      // Apply severity filter
      if (filterBySeverity !== "all" && finding.severity !== filterBySeverity) {
        return false;
      }
      
      // Apply search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          finding.message.toLowerCase().includes(searchLower) ||
          (finding.description && finding.description.toLowerCase().includes(searchLower)) ||
          finding.category.toLowerCase().includes(searchLower) ||
          (finding.subcategory && finding.subcategory.toLowerCase().includes(searchLower))
        );
      }
      
      return true;
    });
  }, [findings, searchTerm, filterBySeverity]);

  // Count findings by severity
  const severityCounts = useMemo(() => {
    const counts = {
      [SeverityLevel.CRITICAL]: 0,
      [SeverityLevel.HIGH]: 0,
      [SeverityLevel.MEDIUM]: 0,
      [SeverityLevel.LOW]: 0,
      [SeverityLevel.INFO]: 0,
      total: findings.length
    };
    
    findings.forEach(finding => {
      counts[finding.severity]++;
    });
    
    return counts;
  }, [findings]);
  
  // Group findings by category
  const groupedFindings = useMemo(() => {
    const groups: Record<string, Finding[]> = {};
    
    filteredFindings.forEach(finding => {
      const category = finding.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(finding);
    });
    
    return groups;
  }, [filteredFindings]);
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">{title} ({filteredFindings.length})</h2>
        
        <div className="w-full md:w-64">
          <Input
            placeholder="Search findings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <Badge 
          className={`cursor-pointer ${filterBySeverity === "all" 
            ? "bg-primary" 
            : "bg-muted hover:bg-muted/80 text-muted-foreground"
          }`}
          onClick={() => setFilterBySeverity("all")}
        >
          All ({severityCounts.total})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterBySeverity === SeverityLevel.CRITICAL 
            ? "bg-red-500" 
            : "bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
          }`}
          onClick={() => setFilterBySeverity(SeverityLevel.CRITICAL)}
        >
          Critical ({severityCounts[SeverityLevel.CRITICAL]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterBySeverity === SeverityLevel.HIGH 
            ? "bg-orange-500" 
            : "bg-orange-100 hover:bg-orange-200 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 dark:hover:bg-orange-900/50"
          }`}
          onClick={() => setFilterBySeverity(SeverityLevel.HIGH)}
        >
          High ({severityCounts[SeverityLevel.HIGH]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterBySeverity === SeverityLevel.MEDIUM 
            ? "bg-amber-500" 
            : "bg-amber-100 hover:bg-amber-200 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 dark:hover:bg-amber-900/50"
          }`}
          onClick={() => setFilterBySeverity(SeverityLevel.MEDIUM)}
        >
          Medium ({severityCounts[SeverityLevel.MEDIUM]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterBySeverity === SeverityLevel.LOW 
            ? "bg-blue-500" 
            : "bg-blue-100 hover:bg-blue-200 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50"
          }`}
          onClick={() => setFilterBySeverity(SeverityLevel.LOW)}
        >
          Low ({severityCounts[SeverityLevel.LOW]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterBySeverity === SeverityLevel.INFO 
            ? "bg-gray-500" 
            : "bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
          }`}
          onClick={() => setFilterBySeverity(SeverityLevel.INFO)}
        >
          Info ({severityCounts[SeverityLevel.INFO]})
        </Badge>
      </div>
      
      {filteredFindings.length === 0 ? (
        <Card className="p-6 text-center text-muted-foreground">
          No findings match your filters. Try adjusting your search criteria.
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedFindings).map(([category, findings], groupIndex) => (
            <AnimatedContainer key={category} delay={groupIndex * 0.1}>
              <div className="space-y-3">
                <h3 className="text-lg font-medium">{category} ({findings.length})</h3>
                <div className="space-y-2">
                  {findings.map((finding, index) => (
                    <FindingDetails 
                      key={finding.id} 
                      finding={finding} 
                      index={index}
                    />
                  ))}
                </div>
              </div>
            </AnimatedContainer>
          ))}
        </div>
      )}
    </div>
  );
} 