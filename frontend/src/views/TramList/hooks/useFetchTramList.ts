import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ResponseTramData } from "../types";


const fetchTramData = async ():  Promise<ResponseTramData> => {
    const response = await axios.get("http://localhost:8000/api/tram-list/");
  
    return response.data;
  };

const useFetchTramData = () => {
    return useQuery<ResponseTramData>({
      queryKey: ["TramNumber"],
      queryFn: fetchTramData,
    });
};

export default useFetchTramData;