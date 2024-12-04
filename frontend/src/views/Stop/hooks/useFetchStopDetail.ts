import { ResponseStopsData } from "../types";
import { useQuery } from '@tanstack/react-query';
import apiClient from "@/services/apiClient/client";


const fetchStopDetailData = async (stop_id: string): Promise<ResponseStopsData> => {
    const response = await apiClient.get(`/stops?stop_id=${stop_id}`);
    return response.data;
};

const useFetchStopDetail = (stop_id: string) => {
    return useQuery<ResponseStopsData>({
        queryKey: ["Stop-detail", stop_id],
        queryFn: () => {
            if (stop_id === 'string') {
                return fetchStopDetailData(stop_id);
            } else {
                return Promise.reject('No stop_id')
            }
        },
        enabled: !!(stop_id),
    });

}

export default useFetchStopDetail;