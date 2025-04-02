import { cn } from "@/lib/utils";
import React from "react";

interface FlexProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  direction?: "row" | "col" | "column";
  mdDirection?: "row" | "col" | "column";
  lgDirection?: "row" | "col" | "column";
  align?: "start" | "center" | "end" | "stretch" | "baseline";
  alignItems?: "start" | "center" | "end" | "stretch" | "baseline";
  justify?: "start" | "center" | "end" | "between" | "around" | "evenly";
  justifyContent?: "start" | "center" | "end" | "between" | "around" | "evenly";
  wrap?: boolean;
  gap?: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16;
  flex?: 1 | "auto" | "initial" | "none";
}

/**
 * A flexible layout component using CSS flexbox with responsive props
 */
export function Flex({
  children,
  className,
  direction = "row",
  mdDirection,
  lgDirection,
  align,
  alignItems,
  justify,
  justifyContent,
  wrap,
  gap,
  flex,
  ...props
}: FlexProps) {
  const normalizeDirection = (dir: string): "row" | "col" => {
    return dir === "column" ? "col" : dir as "row" | "col";
  };

  const normalizedDirection = normalizeDirection(direction);
  const normalizedMdDirection = mdDirection ? normalizeDirection(mdDirection) : undefined;
  const normalizedLgDirection = lgDirection ? normalizeDirection(lgDirection) : undefined;

  const finalAlign = alignItems || align;
  const finalJustify = justifyContent || justify;

  const directionClasses = {
    row: "flex-row",
    col: "flex-col",
  };

  const mdDirectionClasses = normalizedMdDirection
    ? {
        row: "md:flex-row",
        col: "md:flex-col",
      }
    : { row: "", col: "" };

  const lgDirectionClasses = normalizedLgDirection
    ? {
        row: "lg:flex-row",
        col: "lg:flex-col",
      }
    : { row: "", col: "" };

  const alignClasses = finalAlign
    ? {
        start: "items-start",
        center: "items-center",
        end: "items-end",
        stretch: "items-stretch",
        baseline: "items-baseline",
      }
    : { start: "", center: "", end: "", stretch: "", baseline: "" };

  const justifyClasses = finalJustify
    ? {
        start: "justify-start",
        center: "justify-center",
        end: "justify-end",
        between: "justify-between",
        around: "justify-around",
        evenly: "justify-evenly",
      }
    : {
        start: "",
        center: "",
        end: "",
        between: "",
        around: "",
        evenly: "",
      };

  const gapClasses = gap !== undefined
    ? {
        0: "gap-0",
        1: "gap-1",
        2: "gap-2",
        3: "gap-3",
        4: "gap-4",
        5: "gap-5",
        6: "gap-6",
        8: "gap-8",
        10: "gap-10",
        12: "gap-12",
        16: "gap-16",
      }
    : {
        0: "",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        8: "",
        10: "",
        12: "",
        16: "",
      };

  const flexClasses = flex
    ? {
        1: "flex-1",
        auto: "flex-auto",
        initial: "flex-initial",
        none: "flex-none",
      }
    : { 1: "", auto: "", initial: "", none: "" };

  return (
    <div
      className={cn(
        "flex",
        directionClasses[normalizedDirection],
        normalizedMdDirection ? mdDirectionClasses[normalizedMdDirection] : "",
        normalizedLgDirection ? lgDirectionClasses[normalizedLgDirection] : "",
        finalAlign ? alignClasses[finalAlign] : "",
        finalJustify ? justifyClasses[finalJustify] : "",
        wrap ? "flex-wrap" : "",
        gap !== undefined ? gapClasses[gap] : "",
        flex !== undefined ? flexClasses[flex] : "",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
} 