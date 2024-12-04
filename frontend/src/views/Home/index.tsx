import React from "react";
import ButtonAppBar from "@/components/Appbar/Appbar";
import HomeButton from "./components/Buttons/MainButtons";
import DigitalClock from "@/components/DigitalClock/DigitalClock";
import styles from "./styles.module.scss";

const Home = () => {

  return (
    <>
      <ButtonAppBar />
      <div className={styles['digital-clock']}>
        <DigitalClock />
      </div>
      <div className={styles['home-buttons']}>
        <HomeButton />
      </div>
    </>
  );
}

export default Home;