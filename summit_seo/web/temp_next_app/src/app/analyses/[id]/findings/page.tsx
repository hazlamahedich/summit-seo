"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { AnimatedContainer } from "@/components/ui/animated-container";
import { FindingsList } from "@/components/analyses/findings-list";
import { RecommendationsList } from "@/components/analyses/recommendations-list";
import { Finding, Recommendation, SeverityLevel, RecommendationPriority } from "@/types/api";

interface AnalysisDetailsResponse {
  findings: Finding[];
  recommendations: Recommendation[];
}

export default function FindingsAndRecommendationsPage() {
  const params = useParams();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AnalysisDetailsResponse | null>(null);
  const [activeTab, setActiveTab] = useState("findings");

  // Fetch analysis data
  useEffect(() => {
    const fetchAnalysisDetails = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call when available
        const mockFindings: Finding[] = [
          {
            id: "f1",
            analysis_id: params.id as string,
            analyzer: "security",
            category: "Security",
            subcategory: "HTTPS",
            severity: SeverityLevel.CRITICAL,
            message: "Website is not using HTTPS",
            description: "The website is not using secure HTTPS protocol. This poses security risks and negatively impacts SEO rankings.",
            location: "https://example.com",
            details: {
              impact: "High",
              browser_warning: true
            },
            created_at: new Date().toISOString()
          },
          {
            id: "f2",
            analysis_id: params.id as string,
            analyzer: "seo",
            category: "SEO",
            subcategory: "Meta Tags",
            severity: SeverityLevel.HIGH,
            message: "Missing meta descriptions on multiple pages",
            description: "7 pages are missing meta descriptions, which are important for search engine result pages.",
            location: null,
            details: {
              affected_pages: [
                "https://example.com/about",
                "https://example.com/contact",
                "https://example.com/services"
              ]
            },
            created_at: new Date().toISOString()
          },
          {
            id: "f3",
            analysis_id: params.id as string,
            analyzer: "performance",
            category: "Performance",
            subcategory: "Load Time",
            severity: SeverityLevel.MEDIUM,
            message: "Slow page load time",
            description: "Average page load time is 4.2 seconds, exceeding the recommended 3 seconds.",
            location: null,
            details: {
              average_load_time: 4.2,
              recommended_time: 3.0
            },
            created_at: new Date().toISOString()
          },
          {
            id: "f4",
            analysis_id: params.id as string,
            analyzer: "accessibility",
            category: "Accessibility",
            subcategory: "Images",
            severity: SeverityLevel.LOW,
            message: "Images missing alt text",
            description: "12 images are missing alt text, making them inaccessible to screen readers.",
            location: null,
            details: {
              affected_images: 12,
              total_images: 45
            },
            created_at: new Date().toISOString()
          }
        ];

        const mockRecommendations: Recommendation[] = [
          {
            id: "r1",
            analysis_id: params.id as string,
            finding_id: "f1",
            analyzer: "security",
            category: "Security",
            type: "ssl_installation",
            priority: RecommendationPriority.CRITICAL,
            title: "Enable HTTPS for all pages",
            description: "Install an SSL certificate and configure your web server to use HTTPS for all pages.",
            steps: [
              "Purchase an SSL certificate from a trusted provider",
              "Install the certificate on your web server",
              "Configure your web server to redirect HTTP to HTTPS",
              "Update internal links to use HTTPS"
            ],
            resources: [
              "https://letsencrypt.org/getting-started/",
              "https://web.dev/why-https-matters/"
            ],
            details: {
              estimated_time: "2-4 hours",
              difficulty: "Moderate"
            },
            created_at: new Date().toISOString(),
            enhanced: true,
            enhanced_description: "HTTPS is critical for website security and user trust. It encrypts data transferred between your server and visitors, protects sensitive information, and is a ranking factor for search engines. Modern browsers also display warnings for non-HTTPS sites, potentially driving away visitors."
          },
          {
            id: "r2",
            analysis_id: params.id as string,
            finding_id: "f2",
            analyzer: "seo",
            category: "SEO",
            type: "meta_descriptions",
            priority: RecommendationPriority.HIGH,
            title: "Add meta descriptions to all pages",
            description: "Create unique, descriptive meta descriptions for all pages missing them.",
            steps: [
              "Identify all pages missing meta descriptions",
              "Write unique, compelling descriptions of 150-160 characters for each page",
              "Include relevant keywords naturally in the descriptions",
              "Add the meta descriptions to your pages' HTML"
            ],
            resources: [
              "https://moz.com/learn/seo/meta-description",
              "Examples of effective meta descriptions"
            ],
            details: {
              estimated_time: "1-3 hours",
              difficulty: "Easy"
            },
            created_at: new Date().toISOString(),
            enhanced: true,
            enhanced_description: "Meta descriptions don't directly impact rankings but significantly affect click-through rates from search results. Well-crafted descriptions act as organic ad copy, convincing users to visit your site. They should accurately summarize page content while enticing users to click."
          },
          {
            id: "r3",
            analysis_id: params.id as string,
            finding_id: "f3",
            analyzer: "performance",
            category: "Performance",
            type: "page_speed",
            priority: RecommendationPriority.MEDIUM,
            title: "Optimize page load speed",
            description: "Implement performance optimizations to reduce page load time.",
            steps: [
              "Optimize and compress images",
              "Enable browser caching",
              "Minify CSS, JavaScript, and HTML",
              "Use a content delivery network (CDN)",
              "Reduce server response time"
            ],
            resources: [
              "https://web.dev/fast/",
              "https://developers.google.com/speed/pagespeed/insights/"
            ],
            details: {
              estimated_time: "3-8 hours",
              difficulty: "Moderate to Advanced"
            },
            created_at: new Date().toISOString(),
            enhanced: false,
            enhanced_description: null
          },
          {
            id: "r4",
            analysis_id: params.id as string,
            finding_id: "f4",
            analyzer: "accessibility",
            category: "Accessibility",
            type: "alt_text",
            priority: RecommendationPriority.LOW,
            title: "Add alt text to all images",
            description: "Add descriptive alt text to all images missing this attribute.",
            steps: [
              "Identify all images missing alt text",
              "Write descriptive alt text for each image",
              "Implement the alt text in your HTML",
              "Verify implementation with screen readers"
            ],
            resources: [
              "https://webaim.org/techniques/alttext/",
              "Alt text examples and best practices"
            ],
            details: {
              estimated_time: "1-2 hours",
              difficulty: "Easy"
            },
            created_at: new Date().toISOString(),
            enhanced: false,
            enhanced_description: null
          }
        ];
        
        setData({
          findings: mockFindings,
          recommendations: mockRecommendations
        });
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching analysis details:", error);
        setLoading(false);
      }
    };

    if (params.id) {
      fetchAnalysisDetails();
    }
  }, [params.id]);

  if (loading) {
    return <div className="p-8">Loading findings and recommendations...</div>;
  }

  if (!data) {
    return <div className="p-8">Failed to load analysis details</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Findings & Recommendations</h1>
        <p className="text-muted-foreground">
          Detailed analysis results with actionable recommendations
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="findings">Findings ({data.findings.length})</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations ({data.recommendations.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="findings" className="space-y-4">
          <AnimatedContainer>
            <Card className="p-6">
              <FindingsList findings={data.findings} />
            </Card>
          </AnimatedContainer>
        </TabsContent>
        
        <TabsContent value="recommendations" className="space-y-4">
          <AnimatedContainer>
            <Card className="p-6">
              <RecommendationsList recommendations={data.recommendations} />
            </Card>
          </AnimatedContainer>
        </TabsContent>
      </Tabs>
    </div>
  );
} 