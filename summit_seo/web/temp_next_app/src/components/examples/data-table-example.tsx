"use client"

import React from 'react';
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableFooter,
  TableHead, 
  TableRow, 
  TableCell, 
  TableCaption 
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface DataItem {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'success' | 'failed';
  date: string;
  score: number;
}

export function DataTableExample() {
  const { toast } = useToast();
  
  // Example data
  const data: DataItem[] = [
    { id: '1', name: 'example.com', status: 'success', date: '2023-05-10', score: 87 },
    { id: '2', name: 'mywebsite.org', status: 'pending', date: '2023-05-11', score: 65 },
    { id: '3', name: 'blog.example.net', status: 'processing', date: '2023-05-09', score: 72 },
    { id: '4', name: 'store.mycompany.com', status: 'failed', date: '2023-05-08', score: 43 },
    { id: '5', name: 'portfolio.dev', status: 'success', date: '2023-05-07', score: 91 },
  ];
  
  const handleRowClick = (item: DataItem) => {
    toast({
      title: `Selected: ${item.name}`,
      description: `Score: ${item.score}, Status: ${item.status}`,
      duration: 3000,
    });
  };
  
  const getStatusColor = (status: DataItem['status']) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'processing':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
      default:
        return '';
    }
  };
  
  return (
    <div className="rounded-md border">
      <Table>
        <TableCaption>Recent Analysis Results</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">ID</TableHead>
            <TableHead>Website</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Score</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow 
              key={item.id} 
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => handleRowClick(item)}
            >
              <TableCell className="font-medium">{item.id}</TableCell>
              <TableCell>{item.name}</TableCell>
              <TableCell>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                  {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                </span>
              </TableCell>
              <TableCell>{item.date}</TableCell>
              <TableCell className="text-right">{item.score}%</TableCell>
              <TableCell className="text-right">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    toast({
                      title: "Viewing details",
                      description: `Opening details for ${item.name}`,
                      variant: "info",
                    });
                  }}
                >
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell colSpan={3}>Totals</TableCell>
            <TableCell>5 analyses</TableCell>
            <TableCell className="text-right">
              {(data.reduce((acc, item) => acc + item.score, 0) / data.length).toFixed(1)}%
            </TableCell>
            <TableCell className="text-right">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  toast({
                    title: "Export data",
                    description: "Exporting analysis results...",
                    variant: "success",
                  });
                }}
              >
                Export
              </Button>
            </TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    </div>
  );
} 