import { cn } from "@/lib/utils";
import React from "react";
import { Container } from "./container";
import { Flex } from "./flex";
import { Grid, GridItem } from "./grid";

interface FooterProps extends React.HTMLAttributes<HTMLElement> {
  children?: React.ReactNode;
  containerSize?: "sm" | "md" | "lg" | "xl" | "full";
  logo?: React.ReactNode;
  simple?: boolean;
}

/**
 * A responsive footer component
 */
export function Footer({
  children,
  className,
  containerSize = "lg",
  logo,
  simple = false,
  ...props
}: FooterProps) {
  if (simple) {
    return (
      <footer
        className={cn("py-6 border-t bg-muted/30", className)}
        {...props}
      >
        <Container size={containerSize}>
          <Flex align="center" justify="between" wrap>
            <div className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} Summit SEO. All rights reserved.
            </div>
            {logo && <div>{logo}</div>}
          </Flex>
        </Container>
      </footer>
    );
  }

  return (
    <footer
      className={cn("py-12 border-t bg-muted/30", className)}
      {...props}
    >
      <Container size={containerSize}>
        <Grid cols={{ default: 1, md: 2, lg: 4 }} gap={8} className="mb-8">
          {children}
        </Grid>
        
        <div className="border-t pt-8 mt-4">
          <Flex align="center" justify="between" mdDirection="row" direction="col" gap={4}>
            <div className="text-sm text-muted-foreground order-2 md:order-1">
              &copy; {new Date().getFullYear()} Summit SEO. All rights reserved.
            </div>
            {logo && <div className="order-1 md:order-2">{logo}</div>}
          </Flex>
        </div>
      </Container>
    </footer>
  );
}

interface FooterSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
}

/**
 * A footer section component for organizing content in the footer
 */
export function FooterSection({
  children,
  className,
  title,
  ...props
}: FooterSectionProps) {
  return (
    <div className={cn("flex flex-col", className)} {...props}>
      {title && (
        <h3 className="font-medium text-sm tracking-wide uppercase mb-3">
          {title}
        </h3>
      )}
      <ul className="space-y-2">
        {React.Children.map(children, (child) => {
          return <li>{child}</li>;
        })}
      </ul>
    </div>
  );
} 