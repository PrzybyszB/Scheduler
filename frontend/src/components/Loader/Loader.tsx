import React from 'react';
import styles from './styles.module.scss';

const Loader = () => {
    return (
        <>
            <p className={styles["p-container"]}>
                We have server resources problem.
                <br/>
                Please be patient...
                <br/>
                <br/>
                <br/>
                Data is coming for you 🙂
            </p>
            <div className={styles["loader-container"]}>
                <img src="/metro_gif.gif" alt="Ładowanie..." />
            </div>
        </>
    );
};

export default Loader;