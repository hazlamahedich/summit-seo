import React from "react";
import { Container } from "@/components/ui/container";
import { Card } from "@/components/ui/card";
import { Grid } from "@/components/ui/grid";
import Link from "next/link";
import { ArrowRight, Smartphone, Palette, Layout, Zap } from "lucide-react";

export default function ExamplesPage() {
  const examples = [
    {
      title: "Responsive Design",
      description: "Examples of responsive layouts for different screen sizes",
      icon: <Smartphone className="h-6 w-6" />,
      href: "/examples/responsive",
      color: "bg-blue-100 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
      iconColor: "text-blue-600 dark:text-blue-400",
    },
    {
      title: "Animations",
      description: "Interactive components with animations and transitions",
      icon: <Zap className="h-6 w-6" />,
      href: "/examples/animations",
      color: "bg-amber-100 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800",
      iconColor: "text-amber-600 dark:text-amber-400",
    },
    {
      title: "Layout Components",
      description: "Grid, flex, and container layout components",
      icon: <Layout className="h-6 w-6" />,
      href: "/examples/layouts",
      color: "bg-green-100 dark:bg-green-900/20 border-green-200 dark:border-green-800",
      iconColor: "text-green-600 dark:text-green-400",
    },
    {
      title: "Theme Examples",
      description: "Showcase of light and dark theme components",
      icon: <Palette className="h-6 w-6" />,
      href: "/examples/theme",
      color: "bg-purple-100 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800",
      iconColor: "text-purple-600 dark:text-purple-400",
    },
  ];

  return (
    <Container>
      <div className="py-12">
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold mb-4">Component Examples</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A showcase of UI components and responsive design patterns used throughout the application.
          </p>
        </div>

        <Grid 
          cols={{
            default: 1,
            sm: 2,
            lg: 2
          }} 
          gap={6}
          className="max-w-4xl mx-auto"
        >
          {examples.map((example) => (
            <Link href={example.href} key={example.title} className="block group">
              <Card 
                className={`p-6 h-full transition-all ${example.color} hover:shadow-md`}
              >
                <div className="flex items-start gap-4">
                  <div className={`rounded-full p-3 ${example.color} ${example.iconColor}`}>
                    {example.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2 flex items-center group-hover:underline">
                      {example.title}
                      <ArrowRight className="h-4 w-0 ml-2 opacity-0 group-hover:w-4 group-hover:opacity-100 transition-all" />
                    </h3>
                    <p className="text-muted-foreground">
                      {example.description}
                    </p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </Grid>
      </div>
    </Container>
  );
} 