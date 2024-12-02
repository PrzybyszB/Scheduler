import React from "react";
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { useRouter } from 'next/router';
import useFetchBusData from "./hooks/useFetchBusList";
import useHandleButtonClick from "./hooks/useHandleButtonClick";

const BusList = () => {
  const router = useRouter();
  const { data, isLoading, isError } = useFetchBusData();

  const handleButtonClick = useHandleButtonClick();

  if (isLoading) return <p>Ładowanie...</p>;
  if (isError) return <p>Błąd podczas ładowania danych</p>;
  if (!data || data.length === 0) return <p>Nie znaleziono takiego autobusu</p>;

  return (
    <>
      <ButtonAppBar />
        <DigitalClock size="bus-digital-clock" shadow="bus-clock-shadow" />
      <div className={styles["bus-button-grid"]}>
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
      <SideBarNav theme="bus-nav-side-bar" />
    </>
  );
}

export default BusList;