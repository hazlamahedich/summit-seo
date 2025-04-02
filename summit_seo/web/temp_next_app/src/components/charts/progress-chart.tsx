"use client";

import React from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface ProgressMetric {
  name: string;
  value: number;
  goal: number;
  color?: string;
}

interface ProgressChartProps {
  title: string;
  description?: string;
  metrics: ProgressMetric[];
  className?: string;
  showRadar?: boolean;
}

export const ProgressChart: React.FC<ProgressChartProps> = ({
  title,
  description,
  metrics,
  className = "",
  showRadar = true,
}) => {
  // Format data for radar chart
  const radarData = metrics.map((metric) => ({
    subject: metric.name,
    A: metric.value,
    B: metric.goal,
    fullMark: Math.max(metric.goal, metric.value) * 1.2, // 20% buffer above max value
  }));

  // Calculate completion percentages
  const progressItems = metrics.map((metric) => {
    const percentage = Math.min(Math.round((metric.value / metric.goal) * 100), 100);
    return {
      ...metric,
      percentage,
    };
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress bars display */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Progress to Goals</h3>
            <div className="space-y-3">
              {progressItems.map((item, index) => (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.4 }}
                  className="space-y-1"
                >
                  <div className="flex justify-between text-sm">
                    <span>{item.name}</span>
                    <span className="font-medium">
                      {item.value} / {item.goal} ({item.percentage}%)
                    </span>
                  </div>
                  <Progress
                    value={item.percentage}
                    className="h-2"
                    indicatorClassName={item.color ? `bg-[${item.color}]` : ""}
                  />
                </motion.div>
              ))}
            </div>
          </div>

          {/* Radar chart visualization */}
          {showRadar && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="h-[300px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={30} domain={[0, "auto"]} />
                  <Radar
                    name="Current Value"
                    dataKey="A"
                    stroke="var(--primary)"
                    fill="var(--primary)"
                    fillOpacity={0.5}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  />
                  <Radar
                    name="Goal"
                    dataKey="B"
                    stroke="var(--muted-foreground)"
                    fill="var(--muted-foreground)"
                    fillOpacity={0.3}
                    animationDuration={1500}
                    animationEasing="ease-out"
                  />
                  <Legend />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--card)",
                      borderColor: "var(--border)",
                      borderRadius: "var(--radius)",
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}; 