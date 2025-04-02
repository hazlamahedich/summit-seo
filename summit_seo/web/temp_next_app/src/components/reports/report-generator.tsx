"use client";

import React, { useRef, useState } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Loader2, Download, FileText, Printer } from "lucide-react";

interface ReportGeneratorProps {
  title: string;
  description?: string;
  filename?: string;
  orientation?: "portrait" | "landscape";
  paperSize?: "a4" | "letter";
  children: React.ReactNode;
  className?: string;
  showControls?: boolean;
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  title,
  description,
  filename = "report.pdf",
  orientation = "portrait",
  paperSize = "a4",
  children,
  className = "",
  showControls = true,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);

  // Function to generate and download PDF
  const generatePDF = async () => {
    if (!reportRef.current) return;

    setIsGenerating(true);

    try {
      const reportElement = reportRef.current;
      
      // Apply temporary styles for better PDF export
      const chartsElements = reportElement.querySelectorAll('.recharts-wrapper');
      const originalWidths: number[] = [];
      const originalHeights: number[] = [];
      
      // Store original dimensions and set fixed dimensions for export
      chartsElements.forEach((chart, index) => {
        const element = chart as HTMLElement;
        originalWidths[index] = element.style.width ? parseInt(element.style.width) : 0;
        originalHeights[index] = element.style.height ? parseInt(element.style.height) : 0;
        
        // Set fixed dimensions for export
        element.style.width = orientation === 'landscape' ? '450px' : '350px';
        element.style.height = '300px';
      });
      
      // Calculate dimensions based on orientation and paper size
      let width, height;
      if (paperSize === "a4") {
        width = 210; // A4 width in mm
        height = 297; // A4 height in mm
      } else {
        width = 215.9; // Letter width in mm
        height = 279.4; // Letter height in mm
      }
      
      if (orientation === "landscape") {
        [width, height] = [height, width];
      }

      // Create PDF with correct dimensions
      const pdf = new jsPDF({
        orientation: orientation,
        unit: "mm",
        format: paperSize,
      });

      // Add metadata
      pdf.setProperties({
        title: title,
        subject: description || "Report generated from Summit SEO",
        creator: "Summit SEO",
        author: "Summit SEO",
      });

      // Capture HTML content as canvas
      const canvas = await html2canvas(reportElement, {
        scale: 2, // Higher scale for better quality
        useCORS: true,
        logging: false,
        allowTaint: true,
      });

      // Add title and date to PDF
      pdf.setFontSize(18);
      pdf.text(title, 14, 22);
      
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Generated on ${new Date().toLocaleString()}`, 14, 30);
      
      if (description) {
        pdf.text(description, 14, 38);
      }

      // Add canvas image to PDF
      const imgData = canvas.toDataURL("image/png");
      pdf.addImage(imgData, "PNG", 14, description ? 45 : 35, width - 28, 0);

      // Save PDF
      pdf.save(filename);
      
      // Restore original dimensions
      chartsElements.forEach((chart, index) => {
        const element = chart as HTMLElement;
        if (originalWidths[index]) element.style.width = `${originalWidths[index]}px`;
        if (originalHeights[index]) element.style.height = `${originalHeights[index]}px`;
      });
    } catch (error) {
      console.error("Error generating PDF:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Function to print the report
  const printReport = () => {
    window.print();
  };

  return (
    <div className={className}>
      {showControls && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-4 flex flex-wrap gap-2"
        >
          <Button
            onClick={generatePDF}
            disabled={isGenerating}
            className="flex items-center gap-2"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating PDF...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Export as PDF
              </>
            )}
          </Button>
          <Button
            variant="outline"
            onClick={printReport}
            className="flex items-center gap-2"
          >
            <Printer className="h-4 w-4" />
            Print Report
          </Button>
        </motion.div>
      )}

      <div
        ref={reportRef}
        className="report-content bg-card text-card-foreground print:bg-white print:text-black"
        style={{ minHeight: "300px" }}
      >
        <Card className="border-0 shadow-none print:shadow-none">
          <CardHeader className="pb-4">
            <CardTitle className="text-2xl">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </CardHeader>
          <CardContent>
            {children}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}; 