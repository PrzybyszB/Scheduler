import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import Link from 'next/link';
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";

type ResponseRouteData = {
    route_id: string;
    most_popular_patterns: {
        [directionId: string]: {
            stops: {
                stop_name: string;
                stop_id: string;
            }[];
        };
    };
};



const fetchRouteData = async (route_id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`http://localhost:8000/api/${route_id}/`);
 
    return response.data;
};

const RouteDetail = () => { 
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
        <>
            <ButtonAppBar />
            <DigitalClock size="routes-digital-clock" shadow="routes-clock-shadow" />
            <SideBarNav theme="routes-nav-side-bar" />
            <div>
                <ul className={`${styles['route-detail']} ${patterns.length === 1 ? styles['single-index'] : ''}`}>
                    {patterns.map((item) => (
                        <li key={item.directionId} className={styles['direction']}>
                            <h2>
                                <br/>
                                <br/>
                                
                                {item.stops[item.stops.length - 1]?.stop_name}
                            </h2>
                            <br/>
                            
                                <ul className={styles['stops']}>
                                    {item.stops.map((stop) => (
                                        <li key={stop.stop_id} className={styles['stop']}>
                                            <button className={styles['stopButton']}>
                                                {stop.stop_name} 
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            
                        </li>
                    ))}
                </ul>
            </div>
        </>
    );
}

export default RouteDetail;