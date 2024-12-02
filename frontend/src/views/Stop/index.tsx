import React from "react";
import ButtonAppBar from "@/components/Appbar/Appbar";
import { useRouter } from "next/router";
import useFetchStopDetail from "./hooks/useFetchStopDetail";

const StopDetail = () => {
  const router = useRouter();
  const { stop_id } = router.query;

  const { data, isError, isLoading, } = useFetchStopDetail(stop_id as string);
  
  if (isLoading) return <p>Ładowanie...</p>;
  if (isError) return <p>Błąd podczas ładowania strony</p>;
  if (!data) return <p>Nie znaleziono takiego przystanku</p>;

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
