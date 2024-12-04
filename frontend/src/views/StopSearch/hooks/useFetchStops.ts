import { useQuery } from "@tanstack/react-query";
import { ResponseStopsData } from "../types";
import apiClient from "@/services/apiClient/client";

const fetchStopData = async (): Promise<ResponseStopsData> => {
  const response = await apiClient.get("/api/stops/");
  return response.data;
};

const useFetchStops = () => {
  return useQuery<ResponseStopsData>({
    queryKey: ["Stops"],
    queryFn: fetchStopData,
  });
};

export default useFetchStops;
