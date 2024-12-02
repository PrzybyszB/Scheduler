import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ResponseBusData } from "../types";

const fetchBusData = async ():  Promise<ResponseBusData> => {
    const response = await axios.get("http://localhost:8000/api/bus-list/");
  
    return response.data;
  };

const useFetchBusData = () => {
    return useQuery<ResponseBusData>({
      queryKey: ["BusNumber"],
      queryFn: fetchBusData,
    });
};

export default useFetchBusData;