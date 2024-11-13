import { StopData } from "../types";

const useFilteredStops = (stops: StopData[] | undefined, query: string) => {
  if (!stops) return [];

  return stops.filter((stop) => {
    const stopNameWithoutDots = stop.stop_name.toLowerCase().replace(".", "");
    const searchQueryWithoutDots = query.toLowerCase().replace(".", "");
    return stopNameWithoutDots.includes(searchQueryWithoutDots);
  });
};

export default useFilteredStops;
