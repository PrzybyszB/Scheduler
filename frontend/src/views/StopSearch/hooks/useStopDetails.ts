import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import axios from "axios";
import { StopData, RouteData } from "../types";

type StopDetailsResponse = {
  stops_data: StopData[];
  routes: RouteData[];
};

const fetchStopDetails = async (stop_id: string): Promise<StopDetailsResponse> => {
  const response = await axios.get(`http://localhost:8000/api/stops/?stop_id=${stop_id}`);
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
