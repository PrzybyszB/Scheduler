import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ResponseTramData } from "../types";
import apiClient from "@/services/apiClient/client";

const fetchTramData = async (): Promise<ResponseTramData> => {
  const response = await apiClient.get("/tram-list/");

  return response.data;
};

const useFetchTramData = () => {
  return useQuery<ResponseTramData>({
    queryKey: ["TramNumber"],
    queryFn: fetchTramData,
  });
};

export default useFetchTramData;