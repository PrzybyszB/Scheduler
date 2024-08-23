import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import styles from "./styles.module.scss";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "../Home/components/DigitalClock/DigitalClock";
import Buttons from "./components/Buttons/Buttons";

type ResponseBusData = {
  route_id: string;
};

const fetchBusData = async (): Promise<ResponseBusData[]> => {
  const response = await axios.get("http://localhost:8000/api/bus-list/");

  return response.data;
};

function BusList() {
  const { data } = useQuery({
    queryKey: ["BusNumber"],
    queryFn: fetchBusData,
  });
  console.log(data);

  if (!data) {
    return <p>No data found</p>;
  }

  return (
    <>
      <ButtonAppBar />
      <div className={styles["clock-container"]}>
        <DigitalClock fontSize="4rem" />
      </div>
      <div className={styles["home-buttons"]}>
        <Buttons/>
      </div>
      <div className={styles["bus-button-grid"]}>
        {/* Itereting by function map through data. For each element 'route' in table, we create new element TSX*/}
        {data.map((route) => (
          // Create element <button> with unique key assigned to route.route_id. {route.route_id} is a text in the button
          <button key={route.route_id} className={styles["list-button"]}>
            {route.route_id}
          </button>
        ))}
      </div>
    </>
  );
}

export default BusList;
