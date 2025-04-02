"use client";

import React from "react";
import { motion } from "framer-motion";

interface ScoreCircleProps {
  score: number;
  size?: number;
  thickness?: number;
  className?: string;
}

export const ScoreCircle: React.FC<ScoreCircleProps> = ({
  score,
  size = 120,
  thickness = 8,
  className = "",
}) => {
  // Ensure score is between 0 and 100
  const normalizedScore = Math.max(0, Math.min(100, score));
  
  // Calculate colors based on score
  const getColor = (score: number) => {
    if (score >= 90) return "#10b981"; // Green for excellent
    if (score >= 70) return "#0ea5e9"; // Blue for good
    if (score >= 50) return "#f59e0b"; // Amber for average
    if (score >= 30) return "#f97316"; // Orange for poor
    return "#ef4444"; // Red for bad
  };

  const color = getColor(normalizedScore);
  
  // Calculate the circumference and stroke-dasharray
  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = `${(normalizedScore / 100) * circumference} ${circumference}`;
  
  // Animation variants
  const circleVariants = {
    hidden: {
      strokeDasharray: `0 ${circumference}`,
    },
    visible: {
      strokeDasharray,
      transition: {
        duration: 1.5,
        ease: "easeOut",
      },
    },
  };

  const scoreVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        delay: 0.5,
        duration: 0.5,
      },
    },
  };

  return (
    <div
      className={`relative flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Background circle */}
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={thickness}
          className="text-muted opacity-25"
        />
      </svg>
      
      {/* Progress circle */}
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ position: "absolute", transform: "rotate(-90deg)" }}
      >
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={thickness}
          strokeLinecap="round"
          variants={circleVariants}
          initial="hidden"
          animate="visible"
        />
      </svg>
      
      {/* Score text */}
      <motion.div
        className="absolute flex flex-col items-center justify-center"
        variants={scoreVariants}
        initial="hidden"
        animate="visible"
      >
        <span className="text-2xl font-bold">{normalizedScore}</span>
        <span className="text-xs text-muted-foreground">Score</span>
      </motion.div>
    </div>
  );
}; 