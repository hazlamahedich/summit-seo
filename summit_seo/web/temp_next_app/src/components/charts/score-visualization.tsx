"use client";

import React from "react";
import {
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { cva } from "class-variance-authority";

interface ScoreData {
  name: string;
  value: number;
  color?: string;
  fullMark?: number;
}

interface ScoreVisualizationProps {
  title: string;
  description?: string;
  scores: ScoreData[];
  type?: "radial" | "pie";
  className?: string;
  showLegend?: boolean;
}

const getColorForScore = (score: number): string => {
  if (score >= 80) return "#10b981"; // green-500
  if (score >= 60) return "#f59e0b"; // amber-500
  return "#ef4444"; // red-500
};

const scoreCardVariants = cva("", {
  variants: {
    size: {
      sm: "max-w-[300px]",
      md: "max-w-[400px]",
      lg: "max-w-full",
    },
  },
  defaultVariants: {
    size: "md",
  },
});

export const ScoreVisualization: React.FC<ScoreVisualizationProps> = ({
  title,
  description,
  scores,
  type = "radial",
  className = "",
  showLegend = true,
}) => {
  // Process data for visualization
  const data = scores.map((score) => ({
    ...score,
    fullMark: score.fullMark || 100,
    fill: score.color || getColorForScore(score.value),
  }));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`${scoreCardVariants()} ${className}`}
    >
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              {type === "radial" ? (
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="20%"
                  outerRadius="80%"
                  barSize={20}
                  data={data}
                  startAngle={180}
                  endAngle={0}
                >
                  <RadialBar
                    label={{ position: "insideStart", fill: "#fff" }}
                    background
                    dataKey="value"
                    animationDuration={1500}
                    animationEasing="ease-out"
                  />
                  {showLegend && <Legend iconSize={10} layout="vertical" verticalAlign="middle" align="right" />}
                  <Tooltip
                    formatter={(value) => [`${value}%`, "Score"]}
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      borderColor: "var(--border)",
                      borderRadius: "var(--radius)",
                    }}
                  />
                </RadialBarChart>
              ) : (
                <PieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, value }) => `${name}: ${value}%`}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  {showLegend && <Legend />}
                  <Tooltip
                    formatter={(value) => [`${value}%`, "Score"]}
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      borderColor: "var(--border)",
                      borderRadius: "var(--radius)",
                    }}
                  />
                </PieChart>
              )}
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}; 