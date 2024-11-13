
import React, { useState } from "react";
import { useRouter } from "next/router";
import ButtonAppBar from "@/components/Appbar/Appbar";
import DigitalClock from "@/components/DigitalClock/DigitalClock";
import Link from "next/link";
import useFetchStops from "./hooks/useFetchStops";
import useStopDetails from "./hooks/useStopDetails";
import useFilteredStops from "./hooks/useFilteredStops";
import useHandleStopClick from "./hooks/useHandleStopClick";
import SmallMap from "./components/SmallMap"; 
import styles from "./styles.module.scss";
import getUniqueRoutes from "./services/getUniqueRoutes";

const StopSearch = () => {
  const router = useRouter();
  const { stop_id } = router.query as { stop_id?: string };

  const { data, isError, isLoading } = useFetchStops();

  const {
    data: stopDetails,
    setStopId,
  } = useStopDetails(stop_id);

  const selectedStop = stopDetails?.stops_data[0];

  const uniqueRouteData = getUniqueRoutes(stopDetails?.routes || []);

  const [newSearch, setNewSearch] = useState("");

  const filteredStops = useFilteredStops(data?.stops_data, newSearch);

  const handleStopClick = useHandleStopClick(setNewSearch, setStopId);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewSearch(event.target.value);
  };

  if (isLoading) return <p>Ładowanie...</p>;
  if (isError) return <p>Błąd podczas ładowania danych</p>;
  if (!data) return <p>Nie znaleziono takiego przystanku</p>;

  return (
    <>
      <ButtonAppBar />
      <div className={styles["digital-clock"]}>
        <DigitalClock />
      </div>
      <div className={styles["main-container"]}>
        <div className={styles["search-container"]}>
          <input
            placeholder="Nazwa przystanku"
            value={newSearch}
            onChange={handleInputChange}
          />
          <button>Szukaj</button>
        </div>

        <div className={styles["hint-container"]}>
          {newSearch.length >= 2 && (
            <ul className={styles["ul-search"]}>
              {filteredStops.map((stop) => (
                <li key={stop.stop_id} onClick={() => handleStopClick(stop)}>
                  {stop.stop_name}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <div className={styles["selected-stop-container"]}>
        {selectedStop && (
          <div>
            <div className={styles["selected-stop-message"]}>
              <div className={styles["route-button-grid"]}>
                {uniqueRouteData.map((route) => (
                  <button className={styles["route-id-button"]} key={route.route_id}>
                    <Link href={`/route/${route.route_id}/stop/${selectedStop.stop_id}/direction/${route.direction_id}`}>
                      {`${route.route_id}`}
                    </Link>
                  </button>
                ))}
              </div>
              <div className={styles['test']}>
                <p>Skrót nazwy: {selectedStop.stop_code}</p>
                <p>Nazwa przystanku: {selectedStop.stop_name}</p>
                <p>Strefa: {selectedStop.zone_id}</p>
              </div>
              <div>
              <SmallMap
                  lat={parseFloat(selectedStop?.stop_lat || "0")}
                  lon={parseFloat(selectedStop?.stop_lon || "0")}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default StopSearch;
