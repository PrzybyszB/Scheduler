import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import ButtonAppBar from "@/components/Appbar/Appbar";
import styles from "./styles.module.scss";
import { useRouter } from "next/router";
import DigitalClock from "@/components/DigitalClock/DigitalClock";

type ResponseStopsData = {
  stops_data:
  [{stop_id: string,
    stop_code: string,
    stop_name: string,
    stop_lat: string,
    stop_lon: string,
    zone_id: string
  }
  ],
  route_id:{
    route_id:[string]
  }
  

};

const fetchStopDetailData = async (stop_id: string): Promise<ResponseStopsData> => {
  const response = await axios.get(`http://localhost:8000/api/stops?stop_id=${stop_id}`);
  return response.data;
};


const StopDetail = () => {
  const router = useRouter();
  const { stop_id } = router.query;

  const { data, isError, isLoading, } = useQuery({
    queryKey: ["Stop-detail", stop_id],
    queryFn: () => {
        if (stop_id === 'string'){
            return fetchStopDetailData(stop_id);
        }else {
            return Promise.reject('No stop_id')
        }
    },
    enabled: !!(stop_id),
  });
  console.log(data)


  if (isLoading) return <p>Ładowanie...</p>;
  if (isError) return <p>Błąd podczas ładowania strony</p>;
  if (!data) {
      return <p>Nie znaleziono takiego przystanku</p>;
  }
  return (
    <>
      <ButtonAppBar />
    <div>
      {data.stops_data[0]?.stop_id}
    </div>
    </>
  );
};

export default StopDetail;
