import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { useRouter } from 'next/router';


type BusData = string[];

const fetchBusData = async ():  Promise<BusData> => {
  const response = await axios.get("http://localhost:8000/api/bus-list/");

  return response.data;
};

function BusList() {
  const router = useRouter();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["BusNumber"],
    queryFn: fetchBusData,
  });
  
  if (isLoading) {
    return <p>Ładowanie...</p>;
  }

  if (isError) {
    return <p>Błąd podczas ładowania danych</p>;
  }

  if (!data || data.length === 0) {
    return <p>Nie znaleziono takiego autobusu</p>;
  }

  const handleButtonClick = (id: string) => {
    router.push(`/route/${id}`);
  };

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
