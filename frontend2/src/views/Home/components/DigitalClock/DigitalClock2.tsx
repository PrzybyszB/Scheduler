import { useState, useEffect } from 'react';
import styles from './styles.module.scss';
import {format} from 'date-fns'

const DigitalClock2 = () => {
    const [time, setTime] = useState<string|null>(null);

    useEffect(() => {
        const intervalID = setInterval(() => {
            setTime(new Date().toISOString());
        }, 1000);

        return () => {
            clearInterval(intervalID);
        };
    }, []);

    if(!time) {
        return null;
    }

    return (
        <div className={styles['body-container-2']}>
            <div className={styles['clock-container-2']}>
                <div className={styles['clock-2']}>
                    <span className={styles['clock-span-2']}>{format(new Date(time), "HH:mm:ss")}</span>
                </div>
            </div>
        </div>
    );
}

export default DigitalClock2;