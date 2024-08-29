import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import ButtonAppBar from "@/components/Appbar/Appbar";
import styles from "./styles.module.scss";
import DigitalClock from "../../components/DigitalClock/DigitalClock";
import SideBarNav from "@/components/SideBarNav/SideBarNav";
import { useRouter } from 'next/router';

type ResponseTramData = {
  route_id: string;
};

const fetchTramData = async (): Promise<ResponseTramData[]> => {
  const response = await axios.get("http://localhost:8000/api/tram-list/");

  return response.data;
};



function TramList() {
  const router = useRouter();
  const { data } = useQuery({
    queryKey: ["TramNumber"],
    queryFn: fetchTramData,
  });
  console.log(data);
  
  if (!data) {
    return <p>No data found</p>;
  }
  
  const handleButtonClick = (id: string) => {
    router.push(`/${id}`);
  };
  

  return (
    <>
       <ButtonAppBar />
       <DigitalClock size="tram-digital-clock" shadow="tram-clock-shadow"  />
      <div className={styles["tram-button-grid"]}>
        {/* Itereting by function map through data. For each element 'route' in table, we create new element TSX*/}
        {data.map((route) => (
          // Create element <button> with unique key assigned to route.route_id. {route.route_id} is a text in the button
          <button key={route.route_id} 
          className={styles["list-button"]}
          onClick={() => handleButtonClick(route.route_id)}>
              {route.route_id}
            </button>
        ))}
      </div>
      <SideBarNav theme="tram-nav-side-bar" />
    </>
  );
}

export default TramList;
