"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { useResponsive } from "@/contexts/responsive-context";

interface ResponsiveImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  priority?: boolean;
  fallbackSrc?: string;
  lowQualitySrc?: string;
  mobileWidth?: number;
  mobileHeight?: number;
  mobileSrc?: string;
  tabletSrc?: string;
  desktopSrc?: string;
  loadingStrategy?: "eager" | "lazy" | "progressive";
  aspectRatio?: string;
  objectFit?: "contain" | "cover" | "fill" | "none" | "scale-down";
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * Responsive image component with mobile optimization features
 */
export function ResponsiveImage({
  src,
  alt,
  className,
  width,
  height,
  priority = false,
  fallbackSrc = "/images/placeholder.jpg",
  lowQualitySrc,
  mobileWidth,
  mobileHeight,
  mobileSrc,
  tabletSrc,
  desktopSrc,
  loadingStrategy = "progressive",
  aspectRatio = "auto",
  objectFit = "cover",
  onLoad,
  onError,
}: ResponsiveImageProps) {
  const { deviceType, isMobile, isTablet, isDesktop } = useResponsive();
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [showLowQuality, setShowLowQuality] = useState(Boolean(lowQualitySrc));
  
  // Determine appropriate image source based on device type
  const getSourceForDevice = () => {
    if (hasError) return fallbackSrc;
    
    if (isMobile && mobileSrc) return mobileSrc;
    if (isTablet && tabletSrc) return tabletSrc;
    if (isDesktop && desktopSrc) return desktopSrc;
    
    return src;
  };
  
  // Determine appropriate dimensions based on device type
  const getDimensions = () => {
    if (isMobile && mobileWidth && mobileHeight) {
      return { width: mobileWidth, height: mobileHeight };
    }
    
    if (width && height) {
      return { width, height };
    }
    
    // Default dimensions
    return { width: 1200, height: 800 };
  };
  
  // Get current image source
  const currentSrc = getSourceForDevice();
  const dimensions = getDimensions();
  
  // Progressive loading effect
  useEffect(() => {
    if (loadingStrategy === "progressive" && lowQualitySrc && isLoaded) {
      // Fade out low quality image after high quality is loaded
      const timer = setTimeout(() => {
        setShowLowQuality(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [isLoaded, loadingStrategy, lowQualitySrc]);
  
  // Handle image load event
  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };
  
  // Handle image error event
  const handleError = () => {
    setHasError(true);
    onError?.();
  };
  
  // Determine loading attribute
  const getLoadingAttribute = (): "eager" | "lazy" => {
    if (priority) return "eager";
    if (loadingStrategy === "lazy") return "lazy";
    return "eager"; // For progressive loading, we still want eager loading for the main image
  };
  
  return (
    <div 
      className={cn(
        "relative overflow-hidden", 
        className
      )}
      style={{ aspectRatio }}
    >
      {/* Low quality placeholder image */}
      {showLowQuality && lowQualitySrc && (
        <div className="absolute inset-0 z-0">
          <Image
            src={lowQualitySrc}
            alt={alt}
            fill
            className={cn(
              "transition-opacity duration-500",
              isLoaded ? "opacity-0" : "opacity-100",
              objectFit === "contain" && "object-contain",
              objectFit === "cover" && "object-cover",
              objectFit === "fill" && "object-fill",
              objectFit === "none" && "object-none",
              objectFit === "scale-down" && "object-scale-down",
            )}
            priority
            unoptimized // Often we want to use a very small placeholder
          />
        </div>
      )}
      
      {/* Main image */}
      <Image
        src={currentSrc}
        alt={alt}
        width={dimensions.width}
        height={dimensions.height}
        className={cn(
          "transition-opacity duration-500",
          !isLoaded && "opacity-0",
          isLoaded && "opacity-100",
          objectFit === "contain" && "object-contain",
          objectFit === "cover" && "object-cover",
          objectFit === "fill" && "object-fill",
          objectFit === "none" && "object-none",
          objectFit === "scale-down" && "object-scale-down",
        )}
        onLoad={handleLoad}
        onError={handleError}
        loading={getLoadingAttribute()}
        priority={priority}
      />
    </div>
  );
} 