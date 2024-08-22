import { QueryClient } from '@tanstack/react-query';

let reactQueryClient: QueryClient;

const createQueryClient = () => {
  if (typeof reactQueryClient !== 'undefined') {
    return reactQueryClient;
  }

  reactQueryClient = new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        refetchOnMount: false,
      },
    },
  });

  return reactQueryClient;
};

export const clearReactQueryCache = () => reactQueryClient?.clear();

export default createQueryClient;
