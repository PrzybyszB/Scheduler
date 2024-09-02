import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

type ResponseRouteData = {
    [key: string]: string[];
};

const fetchRouteData = async (id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`http://localhost:8000/api/${id}/`);
 
    return response.data;
};

function RouteDetail() { 
    const router = useRouter();
    const { id } = router.query;

    const { data, isError, isLoading } = useQuery({
        queryKey: ['transport-detail', id],
        queryFn: () => {
            if(id && typeof id === 'string'){
                return fetchRouteData(id);
            } else {
                return Promise.reject('No ID');
            }
        },
        enabled: !!id,
    });

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>Error fetching data</p>;
    if (!data) return <p>No data found</p>;
    
    const patterns = Object.entries(data)
        .map(([key, value]) => ({ pattern: value, count: value.length }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 2);

        return (
            <div>
                <h1>Most Common Patterns:</h1>
                <ul>
                    {patterns.map((item, index) => (
                        <li key={index}>
                            {/* Render the first stop separately */}
                            <h1>{item.pattern[0]}</h1>

                            {item.pattern.slice(0).map((stop, idx) => (
                                <span key={idx}>
                                    {' -> '}
                                    {stop}
                                </span>
                            ))}
                        </li>
                    ))}
                </ul>
            </div>
        );
    }
    
export default RouteDetail;