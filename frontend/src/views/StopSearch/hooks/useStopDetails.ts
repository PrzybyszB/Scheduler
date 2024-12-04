import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { StopData, RouteData } from "../types";
import apiClient from "@/services/apiClient/client";

type StopDetailsResponse = {
  stops_data: StopData[];
  routes: RouteData[];
};

const fetchStopDetails = async (stop_id: string): Promise<StopDetailsResponse> => {
  const response = await apiClient.get(`/stops/?stop_id=${stop_id}`);
  return response.data;
};

const useStopDetails = (initialStopId?: string) => {
  const [stopId, setStopId] = useState(initialStopId);

  const queryResult = useQuery<StopDetailsResponse>({
    queryKey: ["StopDetails", stopId],
    queryFn: () => fetchStopDetails(stopId!),
    enabled: !!stopId,
  });

  return { ...queryResult, setStopId };
};

export default useStopDetails;
