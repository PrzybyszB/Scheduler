import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import usePatterns from './hooks/usePatterns';
import Loader from "@/components/Loader/Loader";

const RouteDetail = () => {
    const router = useRouter();
    const { route_id } = router.query;

    const { patterns, isError, isLoading } = usePatterns(route_id as string);

    if (isLoading) return <Loader/>;
    if (isError) return <p>Błąd podczas ładowania danych</p>;
    if (patterns.length === 0) return <p>Nie znaleziono takiej trasy</p>;

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
                                <br />
                                <br />
                                {'->'} {item.stops[item.stops.length - 1]?.stop_name}
                            </h2>
                            <br />
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
};

export default RouteDetail;
