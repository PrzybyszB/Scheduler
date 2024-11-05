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
        [direction_id: string]: {
            stops: {
                stop_name: string;
                stop_id: string;
            }[];
        };
    };
};



const fetchRouteData = async (route_id: string): Promise<ResponseRouteData> => {
    const response = await axios.get(`http://localhost:8000/api/route/${route_id}/`);
 
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

    if (isLoading) return <p>Ładownie...</p>;
    if (isError) return <p>Błąd podczas ładowania danych</p>;
    if (!data) return <p>Nie znaleziono takiej trasy</p>;
    
    const patterns = Object.entries(data.most_popular_patterns).map(([direction_id, { stops }]) => ({
        direction_id,
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
                        <li key={item.direction_id} className={styles['direction']}>
                            <h2>
                                <br/>
                                <br/>
                                
                                {'->'} {item.stops[item.stops.length - 1]?.stop_name}
                            </h2>
                            <br/>
                                <ul className={styles['stops']}>
                                    
                                        {item.stops.map((stop) => (
                                            <li key={stop.stop_id} className={styles['stop']}>
                                                <Link href={`/route/${route_id}/stop/${stop.stop_id}/direction/${item.direction_id}`}>
                                                <button className={styles['stopButton']}>
                                                    {stop.stop_name} 
                                                </button>
                                                </Link>
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