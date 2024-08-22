import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

type ResponseTramData = {
  route_id: string;
};

const fetchTramData = async (): Promise<ResponseTramData[]> => {
  const response = await axios.get("http://localhost:8000/api/tram-list/");

  return response.data;
};

function TramList() {

  const { data } = useQuery({
    queryKey: ["TramNumber"],
    queryFn: fetchTramData,
  });
  console.log(data)

  if (!data) {
    return <p>No data found</p>;
  }

  return (
    <div>
      {data.map((route) => (
        <div key={route.route_id}>
          <h1>Tram Number: {route.route_id}</h1>
        </div>
      ))}
    </div>
  );
}


export default TramList;
