import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

type ResponseRouteData = {
    route_id: string;
    most_popular_patterns: {
        [directionId: string]: {
            stops: string[];
        };
    };
};


const fetchRouteData = async (route_id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`http://localhost:8000/api/${route_id}/`);
 
    return response.data;
};

function RouteDetail() { 
    const router = useRouter();
    const { route_id } = router.query;

    const { data, isError, isLoading } = useQuery({
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

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>Error fetching data</p>;
    if (!data) return <p>No data found</p>;
    
    const patterns = Object.entries(data.most_popular_patterns).map(([directionId, { stops }]) => ({
        directionId,
        stops,
    }));

    return (
        <div>
            <h1>Rozkład jazdy</h1>
            <ul>
                {patterns.map((item) => (
                    <li key={item.directionId}>
                        <br/>
                        <h3>Kierunek: {item.stops[item.stops.length - 1]}</h3>
                        <span>
                            {item.stops.join(' -> ')}
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
export default RouteDetail;