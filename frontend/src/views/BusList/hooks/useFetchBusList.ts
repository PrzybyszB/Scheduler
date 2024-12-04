import { useQuery } from "@tanstack/react-query";
import apiClient from "@/services/apiClient/client";
import { ResponseBusData } from "../types";

const fetchBusData = async (): Promise<ResponseBusData> => {
  const response = await apiClient.get("/bus-list/");

  return response.data;
};

const useFetchBusData = () => {
  return useQuery<ResponseBusData>({
    queryKey: ["BusNumber"],
    queryFn: fetchBusData,
  });
};

export default useFetchBusData;