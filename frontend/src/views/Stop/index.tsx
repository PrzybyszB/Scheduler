import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import styles from "./styles.module.scss";
import { useState, useEffect } from 'react';
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { daysInWeek } from 'date-fns/constants';
import { scheduler } from 'timers/promises';


type ResponseStopData = {
    current_day: string;
    schedules: Array<{
        route_id: string;
        departure_time: string;
        stop_name: string;
        stop_id: string;
        start_date: string;
        trip_headsign: string;
        direction_id: string;
    }>;
};

const fetchStopData = async (route_id: string, stop_id: string, direction_id: string, day: string): Promise<ResponseStopData> => {
    const response = await axios.get(`http://localhost:8000/api/${route_id}/${stop_id}/${direction_id}?day=${day}`);

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
    const { route_id, stop_id, direction_id } = router.query;

    // State for current selected day
    const [selectedDay, setSelectedDay] = useState<string>('');

    const { data, isError, isLoading, refetch } = useQuery({
        queryKey: ['schedule', route_id, stop_id, direction_id, selectedDay],
        queryFn: () => {
            if (route_id && stop_id && direction_id && typeof route_id === 'string' && typeof stop_id === 'string' && typeof direction_id === 'string') {
                return fetchStopData(route_id, stop_id, direction_id, selectedDay);
            } else {
                return Promise.reject('No route_id or stop_id');
            }
        },
        enabled: !!(route_id && stop_id && direction_id && selectedDay),
    });

    // Set the current day on load
    useEffect(() => {
        const today = new Date();
        const day = today.toLocaleString('en-US', { weekday: 'long' }).toLowerCase();

        // Set the current day
        setSelectedDay(day);
    }, []);

    const handleDayClick = (day: string) => {
        setSelectedDay(day);

        // Fetch new data for the selected day
        refetch();

        router.push(`/${route_id}/${stop_id}/${direction_id}?day=${day}`);
    };

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>Error fetching data</p>;
    if (!data || !data['current_day'] || !data.schedules.length) {
        return <p>No data found</p>;
    }

    const daysInWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

    const sixth = Math.ceil(data.schedules.length / 6);
    const firstColumn = data.schedules.slice(0, sixth);
    const secondColumn = data.schedules.slice(sixth, sixth * 2);
    const thirdColumn = data.schedules.slice(sixth * 2, sixth * 3);
    const fourthColumn = data.schedules.slice(sixth * 3, sixth * 4);
    const fifthColumn = data.schedules.slice(sixth * 4, sixth * 5);
    const sixthColumn = data.schedules.slice(sixth * 5);

    console.log(data.schedules)

    return (
        <>
            <ButtonAppBar />

            <div className={styles['clock-container']}>
                <DigitalClock size="routes-digital-clock" shadow="routes-clock-shadow" />
            </div>
            <div>
                <ul className={styles['days-ul']}>
                    {daysInWeek.map((day) => (
                        <li key={day} className={styles['days-li']}>
                            <button className={`${styles['days-button']} ${selectedDay === day ? styles['active-day'] : ''}`} onClick={() => handleDayClick(day)}>
                                <h1>{getPolishDay(day)}</h1>
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
            <div className={styles['route-number']}>
                <h2>Linia: {data.schedules[0]?.route_id} {data.schedules[0]?.trip_headsign}</h2>
                <br/>
                <h3>Przystanek: {data.schedules[0]?.stop_name}</h3>
            </div>
            <div className={styles['departure-times']}>
                <div className={styles['column']}>
                    {firstColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
                <div className={styles['column']}>
                    {secondColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
                <div className={styles['column']}>
                    {thirdColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
                <div className={styles['column']}>
                    {fourthColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
                <div className={styles['column']}>
                    {fifthColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
                <div className={styles['column']}>
                    {sixthColumn.map((schedule) => (
                        <div key={schedule.route_id} className={styles['time-column']}>
                            <p> {schedule.departure_time}</p>
                        </div>
                    ))}
                </div>
            </div>

        </>
    );
}
export default StopDetail;