import { cn } from "@/lib/utils";
import React from "react";

type ResponsiveColsType = {
  default?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  sm?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  md?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  lg?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  xl?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  "2xl"?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
};

interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | ResponsiveColsType;
  gap?: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16;
  rowGap?: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16;
  colGap?: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16;
}

/**
 * A responsive grid component built on CSS Grid with convenient props for
 * controlling the number of columns at different breakpoints
 */
export function Grid({
  children,
  className,
  cols = 1,
  gap = 4,
  rowGap,
  colGap,
  ...props
}: GridProps) {
  // Helper to get the correct class for number of columns
  const getGridColsClass = (cols: number, prefix: string = ""): string => {
    const breakpoint = prefix ? `${prefix}:` : "";
    const colsMapping: Record<number, string> = {
      1: `${breakpoint}grid-cols-1`,
      2: `${breakpoint}grid-cols-2`,
      3: `${breakpoint}grid-cols-3`,
      4: `${breakpoint}grid-cols-4`,
      5: `${breakpoint}grid-cols-5`,
      6: `${breakpoint}grid-cols-6`,
      7: `${breakpoint}grid-cols-7`,
      8: `${breakpoint}grid-cols-8`,
      9: `${breakpoint}grid-cols-9`,
      10: `${breakpoint}grid-cols-10`,
      11: `${breakpoint}grid-cols-11`,
      12: `${breakpoint}grid-cols-12`,
    };
    return colsMapping[cols] || '';
  };

  // Process responsive cols
  const colClasses: string[] = [];
  
  if (typeof cols === 'object') {
    // Only add classes for breakpoints that are defined
    if (cols.default) colClasses.push(getGridColsClass(cols.default));
    if (cols.sm) colClasses.push(getGridColsClass(cols.sm, 'sm'));
    if (cols.md) colClasses.push(getGridColsClass(cols.md, 'md'));
    if (cols.lg) colClasses.push(getGridColsClass(cols.lg, 'lg'));
    if (cols.xl) colClasses.push(getGridColsClass(cols.xl, 'xl'));
    if (cols['2xl']) colClasses.push(getGridColsClass(cols['2xl'], '2xl'));
  } else {
    // For simple numeric value
    colClasses.push(getGridColsClass(cols));
  }

  const getGapClass = (gap: number): string => {
    const gapMapping: Record<number, string> = {
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
    };
    return gapMapping[gap] || '';
  };

  const getRowGapClass = (gap?: number): string => {
    if (gap === undefined) return "";
    const rowGapMapping: Record<number, string> = {
      0: "row-gap-0",
      1: "row-gap-1",
      2: "row-gap-2",
      3: "row-gap-3",
      4: "row-gap-4",
      5: "row-gap-5",
      6: "row-gap-6",
      8: "row-gap-8",
      10: "row-gap-10",
      12: "row-gap-12",
      16: "row-gap-16",
    };
    return rowGapMapping[gap] || '';
  };

  const getColGapClass = (gap?: number): string => {
    if (gap === undefined) return "";
    const colGapMapping: Record<number, string> = {
      0: "col-gap-0",
      1: "col-gap-1",
      2: "col-gap-2",
      3: "col-gap-3",
      4: "col-gap-4",
      5: "col-gap-5",
      6: "col-gap-6",
      8: "col-gap-8",
      10: "col-gap-10",
      12: "col-gap-12",
      16: "col-gap-16",
    };
    return colGapMapping[gap] || '';
  };

  return (
    <div
      className={cn(
        "grid",
        ...colClasses,
        getGapClass(gap),
        getRowGapClass(rowGap),
        getColGapClass(colGap),
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export interface GridItemProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  colSpan?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | "full";
  mdColSpan?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | "full";
  lgColSpan?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | "full";
}

/**
 * A grid item component that works with the Grid component for defining
 * column spans at different breakpoints
 */
export function GridItem({
  children,
  className,
  colSpan,
  mdColSpan,
  lgColSpan,
  ...props
}: GridItemProps) {
  const getColSpanClass = (span?: number | "full"): string => {
    if (!span) return "";
    if (span === "full") return "col-span-full";
    const spanMapping: Record<number, string> = {
      1: "col-span-1",
      2: "col-span-2",
      3: "col-span-3",
      4: "col-span-4",
      5: "col-span-5",
      6: "col-span-6",
      7: "col-span-7",
      8: "col-span-8",
      9: "col-span-9",
      10: "col-span-10",
      11: "col-span-11",
      12: "col-span-12",
    };
    return spanMapping[span as number] || '';
  };

  const getMdColSpanClass = (span?: number | "full"): string => {
    if (!span) return "";
    if (span === "full") return "md:col-span-full";
    const spanMapping: Record<number, string> = {
      1: "md:col-span-1",
      2: "md:col-span-2",
      3: "md:col-span-3",
      4: "md:col-span-4",
      5: "md:col-span-5",
      6: "md:col-span-6",
      7: "md:col-span-7",
      8: "md:col-span-8",
      9: "md:col-span-9",
      10: "md:col-span-10",
      11: "md:col-span-11",
      12: "md:col-span-12",
    };
    return spanMapping[span as number] || '';
  };

  const getLgColSpanClass = (span?: number | "full"): string => {
    if (!span) return "";
    if (span === "full") return "lg:col-span-full";
    const spanMapping: Record<number, string> = {
      1: "lg:col-span-1",
      2: "lg:col-span-2",
      3: "lg:col-span-3",
      4: "lg:col-span-4",
      5: "lg:col-span-5",
      6: "lg:col-span-6",
      7: "lg:col-span-7",
      8: "lg:col-span-8",
      9: "lg:col-span-9",
      10: "lg:col-span-10",
      11: "lg:col-span-11",
      12: "lg:col-span-12",
    };
    return spanMapping[span as number] || '';
  };

  return (
    <div
      className={cn(
        getColSpanClass(colSpan),
        getMdColSpanClass(mdColSpan),
        getLgColSpanClass(lgColSpan),
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
} 