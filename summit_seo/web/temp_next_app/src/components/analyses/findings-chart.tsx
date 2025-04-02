"use client";

import React from "react";
import { motion } from "framer-motion";

interface FindingCategory {
  name: string;
  count: number;
  color: string;
}

interface FindingsChartProps {
  categories: FindingCategory[];
  maxValue?: number;
}

export const FindingsChart: React.FC<FindingsChartProps> = ({
  categories,
  maxValue,
}) => {
  // Calculate the maximum value for the chart scale if not provided
  const calculatedMax = maxValue || Math.max(...categories.map(cat => cat.count), 1);
  
  return (
    <div className="w-full space-y-3">
      {categories.map((category, index) => (
        <div key={category.name} className="space-y-1">
          <div className="flex justify-between text-sm">
            <span>{category.name}</span>
            <span className="font-medium">{category.count}</span>
          </div>
          <div className="h-4 w-full bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: category.color }}
              initial={{ width: 0 }}
              animate={{ width: `${(category.count / calculatedMax) * 100}%` }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.1,
                ease: "easeOut"
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}; 