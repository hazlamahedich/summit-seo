'use client';

import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { usePreferredMotion } from '@/hooks/usePreferredMotion';

export type AmbientDataMetric = {
  value: number;
  label: string;
  color?: string;
  threshold?: {
    low: number;
    medium: number;
    high: number;
  };
};

export type AmbientAnimationTheme = 
  | 'gradient' 
  | 'particles' 
  | 'waves' 
  | 'glow'
  | 'pulse';

export type AmbientBackgroundProps = {
  className?: string;
  /** Data metrics to influence the animation */
  metrics?: AmbientDataMetric[];
  /** Theme for the background animation */
  theme?: AmbientAnimationTheme;
  /** Whether the animation should respond to data changes */
  responsive?: boolean;
  /** Sensitivity of animation response (0-1) */
  sensitivity?: number;
  /** Whether to use subtle animations even when no data changes */
  ambient?: boolean;
  /** Additional styles for the container */
  style?: React.CSSProperties;
  /** Children components to render on top of the background */
  children?: React.ReactNode;
  /** Z-index value for the background */
  zIndex?: number;
};

export function AmbientBackground({
  className,
  metrics = [],
  theme = 'gradient',
  responsive = true,
  sensitivity = 0.5,
  ambient = true,
  style,
  children,
  zIndex = -1,
}: AmbientBackgroundProps) {
  const [animationState, setAnimationState] = useState({
    intensity: 0,
    dominantColor: metrics[0]?.color || 'rgba(59, 130, 246, 0.5)', // Default blue color
    secondaryColor: 'rgba(199, 210, 254, 0.3)',
  });
  
  // Use a ref to store animation controls to avoid constantly recreating animation instances
  const controlsRef = useRef({
    animate: (props: any) => {},
    start: (props: any) => {},
  });
  
  const prevMetrics = useRef<AmbientDataMetric[]>([]);
  const { preference } = usePreferredMotion();
  const isReducedMotion = preference === 'reduced' || preference === 'none';
  
  // Calculate animation parameters based on metrics
  useEffect(() => {
    if (!responsive || !metrics.length) return;
    
    // Skip if metrics haven't changed to avoid unnecessary re-renders
    if (JSON.stringify(metrics) === JSON.stringify(prevMetrics.current)) return;
    
    prevMetrics.current = [...metrics];
    
    // Calculate overall intensity based on metrics changes
    let totalIntensity = 0;
    let dominantColorValue = '';
    let maxValue = 0;
    
    metrics.forEach(metric => {
      // Normalize metric value based on thresholds or assume 0-100 range
      const normalizedValue = metric.threshold 
        ? normalizeWithThresholds(metric.value, metric.threshold)
        : metric.value / 100;
        
      totalIntensity += normalizedValue * sensitivity;
      
      // Determine dominant color based on highest value metric
      if (metric.value > maxValue && metric.color) {
        maxValue = metric.value;
        dominantColorValue = metric.color;
      }
    });
    
    // Average intensity and clamp between 0-1
    const intensity = Math.min(Math.max(totalIntensity / metrics.length, 0), 1);
    
    setAnimationState({
      intensity,
      dominantColor: dominantColorValue || animationState.dominantColor,
      secondaryColor: createComplementaryColor(dominantColorValue || animationState.dominantColor),
    });
    
    // Trigger animation changes
    updateAnimation(intensity, theme);
  }, [metrics, responsive, sensitivity, theme]);
  
  // Initialize ambient animations if enabled
  useEffect(() => {
    if (!ambient) return;
    
    const interval = setInterval(() => {
      const ambientIntensity = 0.1 + Math.random() * 0.1; // Subtle random intensity
      updateAnimation(ambientIntensity, theme);
    }, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, [ambient, theme]);
  
  // Update the animation based on intensity and theme
  const updateAnimation = (intensity: number, theme: AmbientAnimationTheme) => {
    if (isReducedMotion) {
      // Simplified animations for reduced motion
      controlsRef.current.start({
        opacity: 0.5 + (intensity * 0.2),
        transition: { duration: 2 }
      });
      return;
    }
    
    switch (theme) {
      case 'gradient':
        controlsRef.current.start({
          backgroundPosition: `${100 + intensity * 200}% ${100 + intensity * 100}%`,
          scale: 1 + (intensity * 0.05),
          transition: { duration: 3, ease: 'easeInOut' }
        });
        break;
        
      case 'particles':
        controlsRef.current.start({
          opacity: 0.3 + (intensity * 0.3),
          scale: 1 + (intensity * 0.2),
          transition: { duration: 2 }
        });
        break;
        
      case 'waves':
        controlsRef.current.start({
          y: intensity * 20,
          opacity: 0.4 + (intensity * 0.3),
          transition: { duration: 2, type: 'spring', stiffness: 50 }
        });
        break;
        
      case 'glow':
        controlsRef.current.start({
          boxShadow: `0 0 ${30 + intensity * 100}px ${10 + intensity * 30}px ${animationState.dominantColor}`,
          opacity: 0.4 + (intensity * 0.3),
          transition: { duration: 1.5 }
        });
        break;
        
      case 'pulse':
        controlsRef.current.start({
          scale: [1, 1 + (intensity * 0.1), 1],
          opacity: [0.4, 0.5 + (intensity * 0.2), 0.4],
          transition: { 
            duration: 3, 
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut' 
          }
        });
        break;
    }
  };

  return (
    <div className={cn("relative overflow-hidden", className)} style={style}>
      <motion.div
        className="absolute inset-0 w-full h-full transition-opacity"
        style={{
          zIndex,
          pointerEvents: 'none',
        }}
        initial={{ opacity: 0.4 }}
        animate={{
          opacity: 0.5 + (animationState.intensity * 0.2),
          transition: { duration: 1 }
        }}
        ref={(node) => {
          if (node) {
            controlsRef.current = node;
          }
        }}
      >
        {renderAnimationByTheme(theme, animationState)}
      </motion.div>
      {children}
    </div>
  );
}

// Helper function to normalize values using thresholds
function normalizeWithThresholds(value: number, threshold: { low: number; medium: number; high: number }): number {
  if (value <= threshold.low) return 0.1;
  if (value <= threshold.medium) return 0.5;
  if (value <= threshold.high) return 0.8;
  return 1.0;
}

// Helper function to create a complementary/lighter color
function createComplementaryColor(color: string): string {
  // If it's an rgba color
  if (color.startsWith('rgba')) {
    return color.replace(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/, (_, r, g, b, a) => 
      `rgba(${Math.min(255, parseInt(r) + 40)}, ${Math.min(255, parseInt(g) + 40)}, ${Math.min(255, parseInt(b) + 40)}, ${Math.max(0, parseFloat(a) - 0.2)})`
    );
  }
  
  // If it's a hex color
  if (color.startsWith('#')) {
    const hex = color.slice(1);
    const bigint = parseInt(hex, 16);
    const r = Math.min(255, ((bigint >> 16) & 255) + 40);
    const g = Math.min(255, ((bigint >> 8) & 255) + 40);
    const b = Math.min(255, (bigint & 255) + 40);
    return `rgba(${r}, ${g}, ${b}, 0.3)`;
  }
  
  return 'rgba(199, 210, 254, 0.3)'; // Default light blue
}

// Render different animation themes
function renderAnimationByTheme(theme: AmbientAnimationTheme, state: { intensity: number, dominantColor: string, secondaryColor: string }) {
  switch (theme) {
    case 'gradient':
      return (
        <div 
          className="absolute inset-0 bg-gradient-to-br transition-all duration-1000 ease-in-out"
          style={{ 
            backgroundImage: `linear-gradient(135deg, ${state.dominantColor} 0%, ${state.secondaryColor} 50%, ${state.dominantColor} 100%)`,
            backgroundSize: '200% 200%',
            opacity: 0.3 + (state.intensity * 0.3),
          }}
        />
      );
      
    case 'particles':
      return <ParticlesEffect intensity={state.intensity} color={state.dominantColor} />;
      
    case 'waves':
      return <WavesEffect intensity={state.intensity} color={state.dominantColor} />;
      
    case 'glow':
      return (
        <div 
          className="absolute inset-0 rounded-full blur-3xl transform scale-150 transition-all duration-1000"
          style={{ 
            backgroundColor: state.dominantColor,
            opacity: 0.2 + (state.intensity * 0.2),
          }}
        />
      );
      
    case 'pulse':
      return (
        <div 
          className="absolute inset-0 bg-gradient-to-r transition-all duration-1000"
          style={{ 
            backgroundImage: `radial-gradient(circle at center, ${state.dominantColor} 0%, transparent 70%)`,
            opacity: 0.2 + (state.intensity * 0.3),
          }}
        />
      );
  }
}

// Particle animation component
function ParticlesEffect({ intensity, color }: { intensity: number, color: string }) {
  const count = Math.round(5 + intensity * 15); // More particles with higher intensity
  
  return (
    <div className="absolute inset-0 overflow-hidden">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={`particle-${i}`}
          className="absolute rounded-full"
          initial={{ 
            x: `${Math.random() * 100}%`, 
            y: `${Math.random() * 100}%`,
            opacity: 0.1 + (Math.random() * 0.3),
            scale: 0.2 + (Math.random() * 0.8)
          }}
          animate={{ 
            x: `${Math.random() * 100}%`, 
            y: `${Math.random() * 100}%`,
            opacity: 0.1 + (Math.random() * 0.4 * intensity),
            scale: 0.2 + (Math.random() * intensity)
          }}
          transition={{ 
            duration: 5 + (Math.random() * 10),
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut'
          }}
          style={{ 
            width: `${10 + Math.random() * 20}px`,
            height: `${10 + Math.random() * 20}px`,
            backgroundColor: color,
            filter: 'blur(2px)'
          }}
        />
      ))}
    </div>
  );
}

// Wave animation component
function WavesEffect({ intensity, color }: { intensity: number, color: string }) {
  return (
    <div className="absolute bottom-0 left-0 w-full overflow-hidden">
      <svg 
        className="absolute bottom-0 w-full" 
        style={{ height: `${50 + intensity * 50}px` }}
        viewBox="0 0 1440 320"
        preserveAspectRatio="none"
      >
        <motion.path 
          fill={color}
          fillOpacity={0.3 + (intensity * 0.3)}
          initial={{ d: "M0,224L48,213.3C96,203,192,181,288,176C384,171,480,181,576,202.7C672,224,768,256,864,245.3C960,235,1056,181,1152,170.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" }}
          animate={{ 
            d: [
              "M0,224L48,213.3C96,203,192,181,288,176C384,171,480,181,576,202.7C672,224,768,256,864,245.3C960,235,1056,181,1152,170.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
              "M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,266.7C672,267,768,245,864,213.3C960,181,1056,139,1152,128C1248,117,1344,139,1392,149.3L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
              "M0,160L48,138.7C96,117,192,75,288,69.3C384,64,480,96,576,138.7C672,181,768,235,864,234.7C960,235,1056,181,1152,170.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            ]
          }}
          transition={{ 
            duration: 10 + (5 * intensity),
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut'
          }}
        />
        <motion.path 
          fill={color}
          fillOpacity={0.2 + (intensity * 0.3)}
          initial={{ d: "M0,288L48,272C96,256,192,224,288,213.3C384,203,480,213,576,229.3C672,245,768,267,864,272C960,277,1056,267,1152,234.7C1248,203,1344,149,1392,122.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" }}
          animate={{ 
            d: [
              "M0,288L48,272C96,256,192,224,288,213.3C384,203,480,213,576,229.3C672,245,768,267,864,272C960,277,1056,267,1152,234.7C1248,203,1344,149,1392,122.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
              "M0,256L48,240C96,224,192,192,288,197.3C384,203,480,245,576,261.3C672,277,768,267,864,245.3C960,224,1056,192,1152,160C1248,128,1344,96,1392,80L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z",
              "M0,224L48,229.3C96,235,192,245,288,261.3C384,277,480,299,576,288C672,277,768,235,864,218.7C960,203,1056,213,1152,208C1248,203,1344,181,1392,170.7L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            ]
          }}
          transition={{ 
            duration: 12 + (5 * intensity),
            repeat: Infinity,
            repeatType: 'mirror',
            ease: 'easeInOut',
            delay: 0.5
          }}
        />
      </svg>
    </div>
  );
} 