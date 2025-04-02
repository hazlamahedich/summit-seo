declare module 'next-pwa' {
  import { NextConfig } from 'next';
  
  function withPWA(config?: {
    dest?: string;
    register?: boolean;
    skipWaiting?: boolean;
    disable?: boolean;
    scope?: string;
    sw?: string;
    runtimeCaching?: Array<{
      urlPattern: RegExp;
      handler: string;
      options?: Record<string, any>;
    }>;
    buildExcludes?: Array<string | RegExp>;
    dynamicStartUrl?: boolean;
  }): (nextConfig: NextConfig) => NextConfig;
  
  export = withPWA;
} 