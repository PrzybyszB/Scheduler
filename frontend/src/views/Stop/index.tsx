import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";


type ResponseStopData = {
    current_day: string;
    schedules: Array<{
        route_id : string;
        departure_time : string;
        stop_name : string;
        stop_id : string;
        start_date: string;
    }>;
};

const fetchStopData = async (route_id: string, stop_id: string): Promise<ResponseStopData> => {
    const response = await axios.get(`http://localhost:8000/api/${route_id}/${stop_id}/`);

    return response.data;
};

const StopDetail = () => {
    const router = useRouter();
    const {route_id, stop_id} = router.query;

    const { data, isError, isLoading } = useQuery({
        queryKey: ['schedule', route_id, stop_id],
        queryFn: () => {
            if (route_id && stop_id && typeof route_id === 'string' && typeof stop_id ==='string') {
                return fetchStopData(route_id, stop_id)
            } else {
                return Promise.reject('No route_id or stop_id');
            }
        },
        enabled: !!(route_id && stop_id),
    });

    console.log("Query Data:", data);

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>Error fetching data</p>;
    if (!data || !data['current_day'] || !data.schedules.length) {
        return <p>No data found</p>;
    }

    return (
        <div>
            <h1>Current Day: {data['current_day'].charAt(0).toUpperCase() + data['current_day'].slice(1)}</h1>
            <h2>Schedule: {data.schedules[0]?.route_id}</h2>
            <ul>
                {data.schedules.map((schedule) => (
                    <li key={schedule.stop_id}>
                        Route: {schedule.route_id} | Departure: {schedule.departure_time}
                    </li>
                ))}
            </ul>
        </div>
    );
}
export default StopDetail;