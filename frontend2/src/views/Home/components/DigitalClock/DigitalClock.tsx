import { useState, useEffect } from "react";
import styles from "./styles.module.scss";
import Link from "next/link";
import { format } from "date-fns";

type DigitalClockProps = {
  fontSize?: string;
};

const DigitalClock = ({ fontSize = "8rem" }: DigitalClockProps) => {
  const [time, setTime] = useState<string | null>(null);

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
          <div className={styles["clock"]} style={{ fontSize }}>
            <span className={styles["clock-span"]}>
              {format(new Date(time), "HH:mm:ss")}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default DigitalClock;
