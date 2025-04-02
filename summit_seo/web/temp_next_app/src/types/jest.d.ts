declare namespace jest {
  interface Mock<T = any, Y extends any[] = any[]> {
    (...args: Y): T;
    mockImplementation(fn: (...args: Y) => T): this;
    mockImplementationOnce(fn: (...args: Y) => T): this;
    mockReturnThis(): this;
    mockReturnValue(value: T): this;
    mockReturnValueOnce(value: T): this;
    mockResolvedValue(value: T): this;
    mockResolvedValueOnce(value: T): this;
    mockRejectedValue(value: any): this;
    mockRejectedValueOnce(value: any): this;
    mockClear(): this;
    mockReset(): this;
    mockRestore(): this;
    getMockName(): string;
    mockName(name: string): this;
    mock: {
      calls: Y[];
      instances: T[];
      invocationCallOrder: number[];
      results: Array<{
        type: "return" | "throw";
        value: any;
      }>;
    };
    mockCalls: Y[];
  }

  function fn<T = any, Y extends any[] = any[]>(): Mock<T, Y>;
  function fn<T = any, Y extends any[] = any[]>(implementation: (...args: Y) => T): Mock<T, Y>;

  function requireActual<T = any>(moduleName: string): T;
  function requireMock<T = any>(moduleName: string): T;
  function mock(moduleName: string): void;
  function mock(moduleName: string, factory: () => unknown, options?: {virtual?: boolean}): void;
  function unmock(moduleName: string): void;
  function clearAllMocks(): void;
  function resetAllMocks(): void;
  function restoreAllMocks(): void;
  function advanceTimersByTime(msToRun: number): void;
  function useFakeTimers(): void;
  function useRealTimers(): void;
  function spyOn(object: object, methodName: string): Mock;
  function setTimeout(timeout: number): void;
}

declare function describe(name: string, fn: () => void): void;
describe.only = (name: string, fn: () => void) => {};
describe.skip = (name: string, fn: () => void) => {};

declare function beforeEach(fn: () => void): void;
declare function afterEach(fn: () => void): void;
declare function beforeAll(fn: () => void): void;
declare function afterAll(fn: () => void): void;

declare function test(name: string, fn: () => void, timeout?: number): void;
declare function test(name: string, fn: (done: () => void) => void, timeout?: number): void;
test.only = (name: string, fn: () => void, timeout?: number) => {};
test.skip = (name: string, fn: () => void, timeout?: number) => {};

declare function it(name: string, fn: () => void, timeout?: number): void;
declare function it(name: string, fn: (done: () => void) => void, timeout?: number): void;
it.only = (name: string, fn: () => void, timeout?: number) => {};
it.skip = (name: string, fn: () => void, timeout?: number) => {};

declare function expect<T>(value: T): {
  toBe(expected: any): void;
  toBeInstanceOf(expected: any): void;
  toEqual(expected: any): void;
  toContain(expected: any): void;
  toMatch(expected: string | RegExp): void;
  toBeDefined(): void;
  toBeUndefined(): void;
  toBeTruthy(): void;
  toBeFalsy(): void;
  toBeNull(): void;
  toBeGreaterThan(expected: number): void;
  toBeLessThan(expected: number): void;
  toBeGreaterThanOrEqual(expected: number): void;
  toBeLessThanOrEqual(expected: number): void;
  toHaveBeenCalled(): void;
  toHaveBeenCalledTimes(expected: number): void;
  toHaveBeenCalledWith(...args: any[]): void;
  toHaveBeenLastCalledWith(...args: any[]): void;
  toHaveLength(expected: number): void;
  toHaveProperty(property: string, value?: any): void;
  toBeCloseTo(expected: number, precision?: number): void;
  toBeInTheDocument(): void;
  toHaveClass(className: string): void;
  toHaveAttribute(attr: string, value?: string): void;
  toBeDisabled(): void;
  toBeEnabled(): void;
  toHaveValue(value: any): void;
  not: any;
}; 