import "@/styles/globals.scss";
import type { AppProps } from "next/app";
import AppProvider from "@/providers/AppProvider";

const App = ({ Component, pageProps }: AppProps) => {
  return <AppProvider pageProps={pageProps}><Component {...pageProps} /></AppProvider>;
};

export default App;
