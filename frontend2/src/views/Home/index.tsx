import React from "react";
import ButtonAppBar from "@/components/Appbar/Appbar";
import HomeButton from "./components/Buttons/MainButtons";
import DigitalClock from "./components/DigitalClock/DigitalClock";
import styles from "./styles.module.scss";
import DigitalClock2 from "./components/DigitalClock/DigitalClock2";

const Home = () => {

  return (
    <>
      <div className={styles['app-bar']}>
        <ButtonAppBar />
      </div>
      <div className={styles['digital-clock']}>
        <DigitalClock/>
        <DigitalClock2/>
      </div>
      <div className={styles['home-buttons']}>
        <HomeButton/>
      </div>
    </>
  );
}

export default Home;