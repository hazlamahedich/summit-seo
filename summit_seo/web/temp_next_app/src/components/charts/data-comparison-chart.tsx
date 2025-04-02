"use client";

import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart2, LineChart as LineChartIcon } from "lucide-react";

interface ComparisonData {
  name: string;
  current: number;
  previous: number;
}

interface DataComparisonChartProps {
  title: string;
  description?: string;
  data: ComparisonData[];
  currentLabel?: string;
  previousLabel?: string;
  className?: string;
}

export const DataComparisonChart: React.FC<DataComparisonChartProps> = ({
  title,
  description,
  data,
  currentLabel = "Current",
  previousLabel = "Previous",
  className = "",
}) => {
  const [chartType, setChartType] = useState<"bar" | "line">("bar");

  // Define colors for the chart
  const currentColor = "var(--primary)";
  const previousColor = "var(--muted-foreground)";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <Card className="overflow-hidden">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <CardTitle>{title}</CardTitle>
              {description && <CardDescription>{description}</CardDescription>}
            </div>
            <Tabs
              defaultValue="bar"
              value={chartType}
              onValueChange={(value) => setChartType(value as "bar" | "line")}
              className="h-9"
            >
              <TabsList className="grid w-[120px] grid-cols-2">
                <TabsTrigger value="bar">
                  <BarChart2 className="h-4 w-4" />
                </TabsTrigger>
                <TabsTrigger value="line">
                  <LineChartIcon className="h-4 w-4" />
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AnimatePresence mode="wait">
                <motion.div
                  key={chartType}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="h-full w-full"
                >
                  {chartType === "bar" ? (
                    <BarChart
                      data={data}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          borderColor: "var(--border)",
                          borderRadius: "var(--radius)",
                        }}
                      />
                      <Legend />
                      <Bar
                        dataKey="current"
                        name={currentLabel}
                        fill={currentColor}
                        radius={[4, 4, 0, 0]}
                        animationDuration={1500}
                        animationEasing="ease-out"
                      />
                      <Bar
                        dataKey="previous"
                        name={previousLabel}
                        fill={previousColor}
                        radius={[4, 4, 0, 0]}
                        animationDuration={1500}
                        animationEasing="ease-out"
                      />
                    </BarChart>
                  ) : (
                    <LineChart
                      data={data}
                      margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          borderColor: "var(--border)",
                          borderRadius: "var(--radius)",
                        }}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="current"
                        name={currentLabel}
                        stroke={currentColor}
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        animationDuration={1500}
                        animationEasing="ease-out"
                      />
                      <Line
                        type="monotone"
                        dataKey="previous"
                        name={previousLabel}
                        stroke={previousColor}
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        animationDuration={1500}
                        animationEasing="ease-out"
                      />
                    </LineChart>
                  )}
                </motion.div>
              </AnimatePresence>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}; 