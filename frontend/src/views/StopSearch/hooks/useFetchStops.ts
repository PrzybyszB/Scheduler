import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ResponseStopsData } from "../types";

const fetchStopData = async (): Promise<ResponseStopsData> => {
  const response = await axios.get("http://localhost:8000/api/stops/");
  return response.data;
};

const useFetchStops = () => {
  return useQuery<ResponseStopsData>({
    queryKey: ["Stops"],
    queryFn: fetchStopData,
  });
};

export default useFetchStops;
