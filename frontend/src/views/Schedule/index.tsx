import { useRouter } from 'next/router';
import styles from "./styles.module.scss";
import { useEffect } from 'react';
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import getPolishDay from './hooks/getPolishDay';
import useFetchSchedule from './hooks/useFetchSchedule';
import useDayNavigation from './hooks/useDayNavigation';
import Loader from "@/components/Loader/Loader";
import useCurrentDay from './hooks/useCurrentDay';

const ScheduleDetail = () => {
    const router = useRouter();
    const { route_id, stop_id, direction_id } = router.query;

    // State for current selected day
    const [selectedDay, setSelectedDay] = useCurrentDay();

    const handleDayClick = useDayNavigation(route_id as string, stop_id as string, direction_id as string, setSelectedDay);

    const { data, isError, isLoading, refetch } = useFetchSchedule(route_id as string, stop_id as string, direction_id as string, selectedDay)

    const daysInWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const polishDays = daysInWeek.map((day) => ({
        day,
        label: getPolishDay(day),
    }));

    useEffect(() => {
        if (selectedDay) {
            refetch();
        }
    }, [selectedDay, refetch]);

    if (isLoading) return <Loader/>;
    if (isError) return <p>Błąd podczas ładowania danych</p>;
    if (!data) {
        return <p>Nie znaleziono takiego rozkładu jazdy</p>;
    }

    const sixth = Math.ceil(data.schedule.length / 6);
    const firstColumn = data.schedule.slice(0, sixth);
    const secondColumn = data.schedule.slice(sixth, sixth * 2);
    const thirdColumn = data.schedule.slice(sixth * 2, sixth * 3);
    const fourthColumn = data.schedule.slice(sixth * 3, sixth * 4);
    const fifthColumn = data.schedule.slice(sixth * 4, sixth * 5);
    const sixthColumn = data.schedule.slice(sixth * 5);

    console.log(data.schedule)

    return (
        <>
            <ButtonAppBar />

            <div className={styles['clock-container']}>
                <DigitalClock size="routes-digital-clock" shadow="routes-clock-shadow" />
            </div>
            <div>
                <ul className={styles['days-ul']}>
                    {polishDays.map(({ day, label }) => (
                        <li key={day} className={styles['days-li']}>
                            <button className={`${styles['days-button']} ${selectedDay === day ? styles['active-day'] : ''}`} onClick={() => handleDayClick(day)}>
                                <h1>{label}</h1>
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
            <div className={styles['route-number']}>
                <h2>Linia: {route_id} {'->'} {data.stop_headsign}</h2>
                <br />
                <h3>Przystanek: {data.stop_name}</h3>
            </div>

            <div className={styles['departure-times']}>
                {data.schedule.length === 0 ? (
                    <p className={styles['no-schedule-message']}> Nie ma rozkładu na dany dzień.</p>
                ) : (
                    <>
                        <div className={styles['column']}>
                            {firstColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
                                </div>
                            ))}
                        </div>
                        <div className={styles['column']}>
                            {secondColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
                                </div>
                            ))}
                        </div>
                        <div className={styles['column']}>
                            {thirdColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
                                </div>
                            ))}
                        </div>
                        <div className={styles['column']}>
                            {fourthColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
                                </div>
                            ))}
                        </div>
                        <div className={styles['column']}>
                            {fifthColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
                                </div>
                            ))}
                        </div>
                        <div className={styles['column']}>
                            {sixthColumn.map((time, index) => (
                                <div key={index} className={styles['time-column']}>
                                    <p> {time}</p>
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