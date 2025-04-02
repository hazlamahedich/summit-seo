declare module '@testing-library/react' {
  import { ReactElement } from 'react';

  export interface RenderOptions {
    container?: HTMLElement;
    baseElement?: HTMLElement;
    hydrate?: boolean;
    wrapper?: React.ComponentType<{children: React.ReactNode}>;
  }

  export interface RenderResult {
    container: HTMLElement;
    baseElement: HTMLElement;
    debug: (baseElement?: HTMLElement | HTMLElement[]) => void;
    rerender: (ui: ReactElement) => void;
    unmount: () => void;
    asFragment: () => DocumentFragment;
    findByText: (text: string | RegExp) => Promise<HTMLElement>;
    findAllByText: (text: string | RegExp) => Promise<HTMLElement[]>;
    findByRole: (role: string, options?: {name?: string | RegExp}) => Promise<HTMLElement>;
    findAllByRole: (role: string, options?: {name?: string | RegExp}) => Promise<HTMLElement[]>;
    findByLabelText: (label: string | RegExp) => Promise<HTMLElement>;
    findAllByLabelText: (label: string | RegExp) => Promise<HTMLElement[]>;
    findByPlaceholderText: (placeholder: string | RegExp) => Promise<HTMLElement>;
    findAllByPlaceholderText: (placeholder: string | RegExp) => Promise<HTMLElement[]>;
    findByTestId: (testId: string) => Promise<HTMLElement>;
    findAllByTestId: (testId: string) => Promise<HTMLElement[]>;
    getByText: (text: string | RegExp) => HTMLElement;
    getAllByText: (text: string | RegExp) => HTMLElement[];
    getByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement;
    getAllByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement[];
    getByLabelText: (label: string | RegExp) => HTMLElement;
    getAllByLabelText: (label: string | RegExp) => HTMLElement[];
    getByPlaceholderText: (placeholder: string | RegExp) => HTMLElement;
    getAllByPlaceholderText: (placeholder: string | RegExp) => HTMLElement[];
    getByTestId: (testId: string) => HTMLElement;
    getAllByTestId: (testId: string) => HTMLElement[];
    queryByText: (text: string | RegExp) => HTMLElement | null;
    queryAllByText: (text: string | RegExp) => HTMLElement[];
    queryByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement | null;
    queryAllByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement[];
    queryByLabelText: (label: string | RegExp) => HTMLElement | null;
    queryAllByLabelText: (label: string | RegExp) => HTMLElement[];
    queryByPlaceholderText: (placeholder: string | RegExp) => HTMLElement | null;
    queryAllByPlaceholderText: (placeholder: string | RegExp) => HTMLElement[];
    queryByTestId: (testId: string) => HTMLElement | null;
    queryAllByTestId: (testId: string) => HTMLElement[];
  }

  export const render: (
    ui: ReactElement,
    options?: RenderOptions
  ) => RenderResult;

  export const screen: {
    debug: (baseElement?: HTMLElement | HTMLElement[]) => void;
    findByText: (text: string | RegExp) => Promise<HTMLElement>;
    findAllByText: (text: string | RegExp) => Promise<HTMLElement[]>;
    findByRole: (role: string, options?: {name?: string | RegExp}) => Promise<HTMLElement>;
    findAllByRole: (role: string, options?: {name?: string | RegExp}) => Promise<HTMLElement[]>;
    findByLabelText: (label: string | RegExp) => Promise<HTMLElement>;
    findAllByLabelText: (label: string | RegExp) => Promise<HTMLElement[]>;
    findByPlaceholderText: (placeholder: string | RegExp) => Promise<HTMLElement>;
    findAllByPlaceholderText: (placeholder: string | RegExp) => Promise<HTMLElement[]>;
    findByTestId: (testId: string) => Promise<HTMLElement>;
    findAllByTestId: (testId: string) => Promise<HTMLElement[]>;
    getByText: (text: string | RegExp) => HTMLElement;
    getAllByText: (text: string | RegExp) => HTMLElement[];
    getByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement;
    getAllByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement[];
    getByLabelText: (label: string | RegExp) => HTMLElement;
    getAllByLabelText: (label: string | RegExp) => HTMLElement[];
    getByPlaceholderText: (placeholder: string | RegExp) => HTMLElement;
    getAllByPlaceholderText: (placeholder: string | RegExp) => HTMLElement[];
    getByTestId: (testId: string) => HTMLElement;
    getAllByTestId: (testId: string) => HTMLElement[];
    queryByText: (text: string | RegExp) => HTMLElement | null;
    queryAllByText: (text: string | RegExp) => HTMLElement[];
    queryByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement | null;
    queryAllByRole: (role: string, options?: {name?: string | RegExp}) => HTMLElement[];
    queryByLabelText: (label: string | RegExp) => HTMLElement | null;
    queryAllByLabelText: (label: string | RegExp) => HTMLElement[];
    queryByPlaceholderText: (placeholder: string | RegExp) => HTMLElement | null;
    queryAllByPlaceholderText: (placeholder: string | RegExp) => HTMLElement[];
    queryByTestId: (testId: string) => HTMLElement | null;
    queryAllByTestId: (testId: string) => HTMLElement[];
  };
}

declare module '@testing-library/user-event' {
  interface UserEvent {
    setup(): {
      click: (element: HTMLElement) => Promise<void>;
      type: (element: HTMLElement, text: string) => Promise<void>;
      keyboard: (text: string) => Promise<void>;
      clear: (element: HTMLElement) => Promise<void>;
      selectOptions: (element: HTMLElement, values: string | string[]) => Promise<void>;
      tab: () => Promise<void>;
    };
    click: (element: HTMLElement) => Promise<void>;
    type: (element: HTMLElement, text: string) => Promise<void>;
    keyboard: (text: string) => Promise<void>;
    clear: (element: HTMLElement) => Promise<void>;
    selectOptions: (element: HTMLElement, values: string | string[]) => Promise<void>;
    tab: () => Promise<void>;
  }

  const userEvent: UserEvent;
  export default userEvent;
} 