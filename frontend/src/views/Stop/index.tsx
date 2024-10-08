import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { daysInWeek } from 'date-fns/constants';


type ResponseStopData = {
    current_day: string;
    schedules: Array<{
        route_id : string;
        departure_time : string;
        stop_name : string;
        stop_id : string;
        start_date: string;
        direction_id: string;
    }>;
};

const fetchStopData = async (route_id: string, stop_id: string, direction_id: string): Promise<ResponseStopData> => {
    const response = await axios.get(`http://localhost:8000/api/${route_id}/${stop_id}/${direction_id}`);

    return response.data;
};

const getPolishDay = (day: string): string => {
    const daysMap: { [key: string]: string } = {
        'monday': 'Poniedziałek',
        'tuesday': 'Wtorek',
        'wednesday': 'Środa',
        'thursday': 'Czwartek',
        'friday': 'Piątek',
        'saturday': 'Sobota',
        'sunday': 'Niedziela'
    };
    return daysMap[day] || day;
};

const StopDetail = () => {
    const router = useRouter();
    const {route_id, stop_id, direction_id} = router.query;

    const { data, isError, isLoading } = useQuery({
        queryKey: ['schedule', route_id, stop_id, direction_id],
        queryFn: () => {
            if (route_id && stop_id && typeof route_id === 'string' && typeof stop_id ==='string' && typeof direction_id ==='string') {
                return fetchStopData(route_id, stop_id, direction_id)
            } else {
                return Promise.reject('No route_id or stop_id');
            }
        },
        enabled: !!(route_id && stop_id && direction_id),
    });

    console.log("Query Data:", data);

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>Error fetching data</p>;
    if (!data || !data['current_day'] || !data.schedules.length) {
        return <p>No data found</p>;
    }

    const daysInWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

    return (
        <>
            <ButtonAppBar />
            <DigitalClock size="routes-digital-clock" shadow="routes-clock-shadow" />
    
            <div>
                <ul className={styles['days-ul']}>
                    {daysInWeek.map((day) => (
                        <li key={day} className={styles['days-li']}>
                            <button className={styles['days-button']}>
                                <h1>{getPolishDay(day)}</h1>
                            </button>
                        </li>
                    ))}
                </ul>
                <h2>Linia: {data.schedules[0]?.route_id}</h2>
                <div className={styles['departure-times']}>
                    {data.schedules.map((schedule) => {
                        const [hour, minute] = schedule.departure_time.split(':');
                        return (
                            <div key={schedule.stop_id} className={styles['time-column']}>
                                <h3>{hour}</h3> 
                                <p>{minute}</p>
                            </div>
                        );
                    })}
                </div>
            </div>
        </>
    );
}
export default StopDetail;