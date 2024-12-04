import React from "react";
import ButtonAppBar from "@/components/Appbar/Appbar";
import styles from "./styles.module.scss";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { useRouter } from 'next/router';
import useFetchTramData from "./hooks/useFetchTramList";
import useHandleButtonClick from "./hooks/useHandleButtonClick";
import Loader from "@/components/Loader/Loader";

const TramList = () => {
  const router = useRouter();
  const { data, isLoading, isError } = useFetchTramData();

  const handleButtonClick = useHandleButtonClick();

  if (isLoading) return <Loader/>;
  if (isError) return <p>Błąd podczas ładowania danych</p>;
  if (!data || data.length === 0) return <p>Nie znaleziono takiego tramwaju</p>;

  return (
    <>
      <ButtonAppBar />
      <DigitalClock size="tram-digital-clock" shadow="tram-clock-shadow" />
      <div className={styles["tram-button-grid"]}>
        {/* Itereting by function map through data. For each element 'route' in table, we create new element TSX*/}
        {data.map((route_id) => (
          // Create element <button> with unique key assigned to route.route_id. {route.route_id} is a text in the button
          <button key={route_id}
            className={styles["list-button"]}
            onClick={() => handleButtonClick(route_id)}>
            {route_id}
          </button>
        ))}
      </div>
      <SideBarNav theme="tram-nav-side-bar" />
    </>
  );
}

export default TramList;