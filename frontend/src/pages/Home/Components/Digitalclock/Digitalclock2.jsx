import React, { useState, useEffect } from 'react';
import '/src/pages/Home/Components/Digitalclock/Digitalclock.css';

export default function DigitalClock2() {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const intervalID = setInterval(() => {
            setTime(new Date());
        }, 1000);
        return () => {
            clearInterval(intervalID);
        };
    }, []);

    function formatTime() {
        let hours = time.getHours();
        const minutes = time.getMinutes();
        const seconds = time.getSeconds();
        // const meridiem = hours >= 12 ? "PM" : "AM";

        // hours = hours % 12 || 12;

        return `${padZero(hours)}:${padZero(minutes)}:${padZero(seconds)}`;
    }

    function padZero(number) {
        return (number < 10 ? '0' : '') + number;
    }

    return (
        <div className='body-container-2'>
            <div className='clock-container-2'>
                <div className='clock-2'>
                    <span className='clock-span-2'>{formatTime()}</span>
                </div>
            </div>
        </div>
    );
}