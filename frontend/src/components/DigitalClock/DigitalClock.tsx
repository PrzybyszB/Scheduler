import { useState, useEffect } from "react";
import styles from "./styles.module.scss";
import Link from "next/link";
import { format } from "date-fns";
import cx from 'classnames'

type Props = {
  size?: 'bus-digital-clock' | 'tram-digital-clock' | 'routes-digital-clock';
  shadow?: 'bus-clock-shadow' | 'tram-clock-shadow' | 'routes-clock-shadow';
};



const DigitalClock = ({ size, shadow }: Props) => {
  const [time, setTime] = useState<string | null>(null);

  useEffect(() => {
    setTime(new Date().toISOString());
  },[])

  useEffect(() => {
    const intervalID = setInterval(() => {
      setTime(new Date().toISOString());
    }, 1000);

    return () => {
      clearInterval(intervalID);
    };
  }, []);

  if (!time) {
    return null;
  }

  return (
    <Link href="/" passHref>
      <div className={styles["body-container"]}>
        <div className={styles["clock-container"]}>
          <div className={cx(styles["clock"], styles[`container-${size}`])}>
            <div>
              {format(new Date(time), "HH:mm:ss")}
            </div>
            <div className={cx(styles["clock-shadow"], styles[`container-${shadow}`])}>
              {format(new Date(time), "HH:mm:ss")}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default DigitalClock;
