import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

type ResponseRouteData = {
    patterns: string;
    most_common_patterns: string
};

const fetchRouteData = async (id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`/api/${id}`);
 
    return response.data;
};

function RouteDetail() { 
    
    const router = useRouter();
    const { id } = router.query;

    const {data} = useQuery({
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
    console.log(data)
 
 
    if(!data) {
        return <p>No data found</p>
    }

    return (
        <div>
         
                    <p>Patterns: {data.patterns}</p>
                    <p>Most Common Patterns: {data.most_common_patterns}</p>

       
        </div>
    );
}

export default RouteDetail;