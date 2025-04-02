declare module 'next-router-mock' {
  import { NextRouter } from 'next/router';
  
  const mockRouter: NextRouter;
  export default mockRouter;
  
  export function createURLMock(initialURL: string): {
    pathname: string;
    search: string;
    hash: string;
    parse: () => { [key: string]: string };
    toString: () => string;
  };
  
  export function useRouterMock(): NextRouter;
} 