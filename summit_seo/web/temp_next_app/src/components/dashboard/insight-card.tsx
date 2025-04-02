"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp, Lightbulb, Sparkles, Loader2 } from 'lucide-react';
import { Insight, InsightStatus } from '@/types/api';

interface InsightCardProps {
  insight: Insight;
  className?: string;
  onClick?: () => void;
}

export const InsightCard: React.FC<InsightCardProps> = ({
  insight,
  className,
  onClick
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(cardRef, { once: true, amount: 0.5 });
  
  // Set animation status once in view
  useEffect(() => {
    if (isInView && !hasAnimated) {
      setHasAnimated(true);
    }
  }, [isInView, hasAnimated]);
  
  // Determine card styling based on status
  const getStatusStyles = () => {
    switch (insight.status) {
      case InsightStatus.PENDING:
        return 'border-yellow-200 bg-yellow-50 dark:bg-yellow-950/30 dark:border-yellow-800';
      case InsightStatus.FAILED:
        return 'border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-800';
      case InsightStatus.GENERATED:
      default:
        return 'border-primary/20 bg-primary/5 dark:bg-primary/10 dark:border-primary/30';
    }
  };
  
  // Get the appropriate icon based on insight type
  const getIcon = () => {
    switch (insight.type) {
      case 'performance':
        return <Sparkles className="h-5 w-5 text-primary" />;
      default:
        return <Lightbulb className="h-5 w-5 text-primary" />;
    }
  };
  
  // Animation variants
  const containerVariants = {
    hidden: {
      opacity: 0,
      y: 50,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };
  
  const expandVariants = {
    collapsed: { height: 0, opacity: 0 },
    expanded: { 
      height: "auto", 
      opacity: 1,
      transition: {
        height: {
          duration: 0.3,
        },
        opacity: {
          duration: 0.25,
          delay: 0.15
        }
      }
    }
  };
  
  return (
    <motion.div
      ref={cardRef}
      variants={containerVariants}
      initial="hidden"
      animate={hasAnimated ? "visible" : "hidden"}
      className={cn("relative overflow-hidden", className)}
      onClick={onClick}
    >
      <Card className={cn("relative overflow-hidden transition-all", getStatusStyles())}>
        <CardHeader className="pb-2">
          <motion.div 
            variants={itemVariants} 
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              {getIcon()}
              <CardTitle className="text-lg">
                {insight.title}
              </CardTitle>
            </div>
            
            {insight.status === InsightStatus.PENDING && (
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            )}
          </motion.div>
        </CardHeader>
        
        <CardContent className="pb-0">
          <motion.div variants={itemVariants} className="mb-6">
            <div className="text-sm text-muted-foreground leading-relaxed">
              {!isExpanded 
                ? `${insight.content.substring(0, 150)}${insight.content.length > 150 ? '...' : ''}`
                : insight.content.substring(0, 150)
              }
            </div>
              
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  key="content"
                  initial="collapsed"
                  animate="expanded"
                  exit="collapsed"
                  variants={expandVariants}
                  className="overflow-hidden"
                >
                  <p className="text-sm text-muted-foreground leading-relaxed pt-2">
                    {insight.content.substring(150)}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </CardContent>
        
        <CardFooter>
          <motion.div variants={itemVariants} className="w-full">
            {insight.content.length > 150 && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-xs p-0 h-6"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(!isExpanded);
                }}
              >
                {isExpanded 
                  ? <><ChevronUp className="h-3 w-3 mr-1" /> Read less</> 
                  : <><ChevronDown className="h-3 w-3 mr-1" /> Read more</>
                }
              </Button>
            )}
          </motion.div>
        </CardFooter>
        
        {/* Animated border effect for Generated insights */}
        {insight.status === InsightStatus.GENERATED && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.7 }}
            className="absolute -top-8 -right-8 w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-primary/10 blur-xl"
          />
        )}
      </Card>
    </motion.div>
  );
}; 