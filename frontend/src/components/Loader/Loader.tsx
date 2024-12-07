import React from 'react';
import styles from './styles.module.scss';

const Loader = () => {
    return (
        <>
            <p className={styles["p-container"]}>
                We have server resources problem.
                <br />
                Please be patient...
                <br />
                <br />
                <br />
                Data is coming for you 🙂
            </p>
            <div className={styles["loader-container"]}>
                <div className={styles["sk-fading-circle"]}>
                    <div className={`${styles["sk-circle1"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle2"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle3"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle4"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle5"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle6"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle7"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle8"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle9"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle10"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle11"]} ${styles["sk-circle"]}`}></div>
                    <div className={`${styles["sk-circle12"]} ${styles["sk-circle"]}`}></div>
                </div>
            </div>
        </>
    );
};

export default Loader;



// const Loader = () => {
//     return (
//         <>
// <p className={styles["p-container"]}>
//     We have server resources problem.
//     <br />
//     Please be patient...
//     <br />
//     <br />
//     <br />
//     Data is coming for you 🙂
// </p>
//             <div className={styles["loader-container"]}>
//                 <img src="/metro_gif.gif" alt="Ładowanie..." />
//             </div>
//         </>
//     );
// };

// export default Loader;