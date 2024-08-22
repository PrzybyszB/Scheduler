import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

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
  console.log(data)

  if (!data) {
    return <p>No data found</p>;
  }

  return (
    <div>
      {data.map((route) => (
        <div key={route.route_id}>
          <h1>Bus Number: {route.route_id}</h1>
        </div>
      ))}
    </div>
  );
}


export default BusList;
