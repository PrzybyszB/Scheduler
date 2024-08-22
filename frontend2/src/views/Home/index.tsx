import React, { useState } from "react";
import ButtonAppBar from "@/components/Appbar/Appbar";
import HomeButton from "./components/Buttons/MainButtons";
import DigitalClock from "./components/DigitalClock/DigitalClock";
import DigitalClock2 from "./components/DigitalClock/DigitalClock2";
import styles from "./styles.module.scss";
import MapComponent from "./components/Map/MapComponent";

const Home = () => {

  return (
    <div className={styles["home-container"]}>
      {/* <MapComponent onZoomChange={handleZoomChange} /> */}
      <div className={styles['app-bar']}>
        <ButtonAppBar />
      </div>
      <div className={styles['digital-clock']}>
        <DigitalClock />
        <DigitalClock2 />
      </div>
      <div className={styles['home-buttons']}>
        <HomeButton />
      </div>
    </div>
  );
}

export default Home;