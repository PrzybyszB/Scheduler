import { useQuery } from "@tanstack/react-query";
import axios from 'axios';
import { ResponseRouteData } from '../types';

const fetchRouteData = async (route_id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`http://localhost:8000/api/route/${route_id}/`);
 
    return response.data;
};

const useFetchRouteDetail = (route_id: string) => { 
        return useQuery<ResponseRouteData>({
        queryKey: ['transport-detail', route_id],
        queryFn: () => {
            if(route_id && typeof route_id === 'string'){
                return fetchRouteData(route_id);
            } else {
                return Promise.reject('No ID');
            }
        },
        enabled: !!route_id,
    });
};

export default useFetchRouteDetail;
