import { useQuery } from '@tanstack/react-query';
import { ResponseScheduleData } from '../types';
import apiClient from "@/services/apiClient/client";

const fetchScheduleData = async (route_id: string, stop_id: string, direction_id: string, day: string): Promise<ResponseScheduleData> => {
    const response = await apiClient.get(`/route/${route_id}/stop/${stop_id}/direction/${direction_id}`, {
        params: { day }
    });
    console.log('Fetched schedule data:', response.data);
    return response.data;
};

const useFetchSchedule = (route_id: string, stop_id: string, direction_id: string, selectedDay: string) => {
    return useQuery<ResponseScheduleData>({
        queryKey: ['schedule', route_id, stop_id, direction_id, selectedDay],
        queryFn: () => {
            if (
                route_id &&
                stop_id &&
                direction_id &&
                typeof route_id === 'string' &&
                typeof stop_id === 'string' &&
                typeof direction_id === 'string'
            ) {
                return fetchScheduleData(route_id, stop_id, direction_id, selectedDay);
            } else {
                return Promise.reject('That data does not exist');
            }
        },
        enabled: !!(route_id && stop_id && direction_id && selectedDay),
    });
};


export default useFetchSchedule;