import { QueryClientProvider, HydrationBoundary } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';
import createQueryClient from './createQueryClient';

type Props = {
  initialState: unknown;
  children: React.ReactNode;
}

const ReactQueryProvider = ({ initialState, children }: Props): JSX.Element => {
  const [queryClient] = useState(() => createQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <HydrationBoundary state={initialState}>
        <ReactQueryDevtools />

        {children}
      </HydrationBoundary>
    </QueryClientProvider>
  );
};

export default ReactQueryProvider;
