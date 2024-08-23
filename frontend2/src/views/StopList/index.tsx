import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import ButtonAppBar from "@/components/Appbar/Appbar";
import styles from "@/components/Appbar/styles.module.scss";

type ResponseStopsData = {
  stop_name: string;
};

const fetchTramData = async (): Promise<ResponseStopsData[]> => {
  const response = await axios.get("http://localhost:8000/api/stops-list/");

  return response.data;
};

function StopList() {
  const { data } = useQuery({
    queryKey: ["StopName"],
    queryFn: fetchTramData,
  });
  console.log(data);

  if (!data) {
    return <p>No data found</p>;
  }

  return (
    <>
      <div className={styles["app-bar"]}>
        <ButtonAppBar />
      </div>
      <div>
        {data.map((stops) => (
          <div key={stops.stop_name}>
            <h1>Stop Name: {stops.stop_name}</h1>
          </div>
        ))}
      </div>
    </>
  );
}

export default StopList;
