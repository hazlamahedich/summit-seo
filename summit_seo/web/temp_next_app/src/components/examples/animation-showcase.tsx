"use client";

import React from 'react';
import { 
  AlertCircle, 
  Bell, 
  CheckCircle, 
  ChevronRight, 
  Clock, 
  Heart, 
  HelpCircle,
  Info,
  RotateCw, 
  Search, 
  Settings,
  Star, 
  ThumbsUp 
} from 'lucide-react';
import { motion } from 'framer-motion';
import { AnimatedIcon } from '@/components/ui/animated-icon';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedContainer } from '@/components/ui/animated-container';
import { AnimatedTooltip } from '@/components/ui/animated-tooltip';
import { MotionPreferenceControl } from '@/components/ui/motion-preference-control';
import { Card } from '@/components/ui/card';

export function AnimationShowcase() {
  return (
    <div className="space-y-8 p-6">
      <AnimatedContainer variant="fadeIn">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold mb-2">Animation and Micro-interaction Showcase</h1>
            <p className="text-muted-foreground">
              This page demonstrates various animation patterns and micro-interactions available in the application.
            </p>
          </div>
          
          <div className="space-y-4">
            <div className="flex flex-col items-start gap-2">
              <label className="text-sm font-medium">Motion Preference (Buttons):</label>
              <MotionPreferenceControl variant="buttons" />
            </div>
            <div className="flex flex-col items-start gap-2">
              <label className="text-sm font-medium">Motion Preference (Toggle):</label>
              <MotionPreferenceControl variant="toggle" />
            </div>
            <div className="flex flex-col items-start gap-2">
              <label className="text-sm font-medium">Motion Preference (Select):</label>
              <MotionPreferenceControl variant="select" />
            </div>
          </div>
        </div>
      </AnimatedContainer>

      {/* Icon animations */}
      <AnimatedContainer variant="slideUp" delay={0.1}>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Icon Micro-interactions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon animationType="pulse" size="lg" color="red">
                <Heart className="text-red-500" />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Pulse</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon animationType="rotate" size="lg" color="blue">
                <RotateCw className="text-blue-500" />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Rotate</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon animationType="bounce" size="lg" color="amber">
                <Star className="text-amber-500" />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Bounce</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon animationType="shake" size="lg" color="green">
                <Bell className="text-green-500" />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Shake</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon 
                cycleColors={["#3b82f6", "#ec4899", "#f59e0b", "#10b981"]} 
                size="lg"
              >
                <ThumbsUp />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Color Cycle (Click)</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedIcon hoverEffect={true} clickEffect={true} size="lg">
                <Search />
              </AnimatedIcon>
              <span className="text-sm text-muted-foreground">Hover & Click</span>
            </div>
          </div>
        </Card>
      </AnimatedContainer>

      {/* Tooltip animations */}
      <AnimatedContainer variant="slideUp" delay={0.15}>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Tooltip Micro-interactions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="flex flex-col items-center gap-2">
              <AnimatedTooltip content="Information tooltip" side="top">
                <AnimatedIcon size="lg">
                  <Info className="text-blue-500" />
                </AnimatedIcon>
              </AnimatedTooltip>
              <span className="text-sm text-muted-foreground">Top Tooltip</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedTooltip content="Help information" side="right">
                <AnimatedIcon size="lg">
                  <HelpCircle className="text-purple-500" />
                </AnimatedIcon>
              </AnimatedTooltip>
              <span className="text-sm text-muted-foreground">Right Tooltip</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedTooltip 
                content="Configure settings" 
                side="bottom"
                interactive={true}
              >
                <AnimatedIcon size="lg">
                  <Settings className="text-gray-500" />
                </AnimatedIcon>
              </AnimatedTooltip>
              <span className="text-sm text-muted-foreground">Interactive Tooltip</span>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <AnimatedTooltip 
                content={
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span>Important warning</span>
                  </div>
                } 
                side="left"
                delay={0.2}
              >
                <AnimatedIcon size="lg">
                  <AlertCircle className="text-red-500" />
                </AnimatedIcon>
              </AnimatedTooltip>
              <span className="text-sm text-muted-foreground">Rich Content</span>
            </div>
          </div>
        </Card>
      </AnimatedContainer>

      {/* Button animations */}
      <AnimatedContainer variant="slideUp" delay={0.2}>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Button Interactions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <AnimatedButton>Default Button</AnimatedButton>
            
            <AnimatedButton 
              loading={true}
              loadingText="Loading..."
            >
              Loading State
            </AnimatedButton>
            
            <AnimatedButton
              icon={<CheckCircle className="h-4 w-4" />}
              feedback="success"
            >
              Success Feedback
            </AnimatedButton>
            
            <AnimatedButton
              icon={<AlertCircle className="h-4 w-4" />}
              feedback="error"
            >
              Error Feedback
            </AnimatedButton>
            
            <AnimatedButton
              icon={<Clock className="h-4 w-4" />}
              iconPosition="right"
            >
              Icon Right
            </AnimatedButton>
            
            <AnimatedButton
              variant="outline"
              icon={<ChevronRight className="h-4 w-4" />}
            >
              Outlined Style
            </AnimatedButton>
          </div>
        </Card>
      </AnimatedContainer>

      {/* Container animations */}
      <AnimatedContainer variant="slideUp" delay={0.3}>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Container Animations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Fade Variants</h3>
              <AnimatedContainer 
                variant="fadeIn" 
                className="p-4 border rounded-md"
              >
                <p>Fade In</p>
              </AnimatedContainer>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Slide Variants</h3>
              <div className="space-y-2">
                <AnimatedContainer 
                  variant="slideUp" 
                  className="p-4 border rounded-md"
                >
                  <p>Slide Up</p>
                </AnimatedContainer>
                
                <AnimatedContainer 
                  variant="slideDown" 
                  className="p-4 border rounded-md"
                >
                  <p>Slide Down</p>
                </AnimatedContainer>
                
                <AnimatedContainer 
                  variant="slideLeft" 
                  className="p-4 border rounded-md"
                >
                  <p>Slide Left</p>
                </AnimatedContainer>
                
                <AnimatedContainer 
                  variant="slideRight" 
                  className="p-4 border rounded-md"
                >
                  <p>Slide Right</p>
                </AnimatedContainer>
              </div>
            </div>
          </div>
        </Card>
      </AnimatedContainer>

      {/* Sequential animations */}
      <AnimatedContainer variant="slideUp" delay={0.4}>
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Sequential Animations</h2>
          <motion.div 
            className="space-y-2"
            initial="hidden"
            animate="visible"
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: {
                  staggerChildren: 0.1
                }
              }
            }}
          >
            {[1, 2, 3, 4, 5].map((item) => (
              <motion.div
                key={item}
                className="p-4 border rounded-md"
                variants={{
                  hidden: { opacity: 0, x: -20 },
                  visible: { 
                    opacity: 1, 
                    x: 0,
                    transition: {
                      duration: 0.3
                    }
                  }
                }}
              >
                <p>Item {item}</p>
              </motion.div>
            ))}
          </motion.div>
        </Card>
      </AnimatedContainer>
    </div>
  );
}

export default AnimationShowcase; 