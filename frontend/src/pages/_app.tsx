import "@/styles/globals.scss";
import type { AppProps } from "next/app";
import Head from "next/head";
import AppProvider from "@/providers/AppProvider";

const App = ({ Component, pageProps }: AppProps) => {
  return (
    <>
      <Head>
        <title>Scheduler</title>
      </Head>
      <AppProvider pageProps={pageProps}>
        <Component {...pageProps} />
      </AppProvider>
    </>
  );
};

export default App;