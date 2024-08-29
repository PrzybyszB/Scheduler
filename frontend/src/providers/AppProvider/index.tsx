import { AppProps } from 'next/app';
import ReactQueryProvider from '../ReactQueryProvider';

type Props = {
  pageProps: AppProps<{ initialQueryState?: unknown }>['pageProps'];
  children: React.ReactNode;
}

const AppProvider = ({children,pageProps}: Props) => {
  return (
    <ReactQueryProvider initialState={pageProps.initialQueryState}>
      {children}
    </ReactQueryProvider>
  );
};

export default AppProvider;
 