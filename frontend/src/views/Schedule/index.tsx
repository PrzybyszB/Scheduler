import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import styles from "./styles.module.scss";
import { useState, useEffect } from 'react';
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";


type ResponseScheduleData = {
    current_day: string;
    schedules: Array<{
        route_id: string;
        departure_time: string;
        stop_id: string;
        start_date: string;
        direction_id: string;
    }>;
    stop_name: string;
    stop_headsign: string;
};

const fetchScheduleData = async (route_id: string, stop_id: string, direction_id: string, day: string): Promise<ResponseScheduleData> => {
    const response = await axios.get(`http://localhost:8000/api/route/${route_id}/stop/${stop_id}/direction/${direction_id}`, {
        params: { day } 
    });

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



const ScheduleDetail = () => {
    const router = useRouter();
    const { route_id, stop_id, direction_id } = router.query;

    // State for current selected day
    const [selectedDay, setSelectedDay] = useState<string>('');

    const { data, isError, isLoading, refetch } = useQuery({
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

    // Set the current day on load
    useEffect(() => {
        const today = new Date();
        const day = today.toLocaleString('en-US', { weekday: 'long' }).toLowerCase();

        // Set the current day
        setSelectedDay(day);
    }, []);

    useEffect(() => {
        if (selectedDay) {
            refetch();
        }
    }, [selectedDay, refetch]);

    const handleDayClick = (day: string) => {
        setSelectedDay(day);
        router.push(`/route/${route_id}/stop/${stop_id}/direction/${direction_id}?day=${day}`);
    };

    if (isLoading) return <p>Ładowanie...</p>;
    if (isError) return <p>Błąd podczas ładowania danych</p>;
    if (!data) {
        return <p>Nie znaleziono takiego rozkładu jazdy</p>;
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
                <h2>Linia: {route_id} {'->'} {data.stop_headsign}</h2>
                <br/>
                <h3>Przystanek: {data.stop_name}</h3>
            </div>
            
            <div className={styles['departure-times']}>
                {data.schedules.length === 0 ? (
                        <p className={styles['no-schedule-message']}> Nie ma rozkładu na dany dzień.</p>
                ) : (
                    <>
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
                </>
                )}
            </div>

        </>
    );
}
export default ScheduleDetail;

