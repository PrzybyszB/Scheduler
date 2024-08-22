import { useState, useEffect } from 'react';
import styles from './styles.module.scss';
import {format} from 'date-fns'

const DigitalClock = () => {
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
        <div className={styles['body-container']}>
            <div className={styles['clock-container']}>
                <div className={styles['clock']}>
                    <span className={styles['clock-span']}>{format(new Date(time), "HH:mm:ss")}</span>
                </div>
            </div>
        </div>
    );
}

export default DigitalClock;