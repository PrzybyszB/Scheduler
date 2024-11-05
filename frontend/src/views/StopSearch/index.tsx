import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import ButtonAppBar from "@/components/Appbar/Appbar";
import styles from "./styles.module.scss";
import { useRouter } from "next/router";
import DigitalClock from "@/components/DigitalClock/DigitalClock";
import useSmallMap from "./hooks/useSmallMap";
import Link from 'next/link';



type StopData = {
  stop_id: string;
  stop_code: string;
  stop_name: string;
  stop_lat: string;
  stop_lon: string;
  zone_id: string;
};

type RouteData = {
  route_id: string;
  direction_id: string;
};

type ResponseStopsData = {
  stops_data: StopData[];
  routes: RouteData[];
};

const fetchStopData = async (): Promise<ResponseStopsData> => {
  const response = await axios.get("http://localhost:8000/api/stops/");
  return response.data;
};



const StopSearch = () => {
  const router = useRouter();
  const { stop_id } = router.query
  const { data, isError, isLoading } = useQuery({
    queryKey: ["Stops"],
    queryFn: fetchStopData,
  });

  const [routeData, setRouteData] = useState<RouteData[] | null>(null);
  const [selectedStop, setSelectedStop] = useState<StopData | null>(null);
  const [newSearch, setNewSearch] = useState('');

  useEffect(() => {
    const fetchStopDetails = async () => {
      if (stop_id) {
        const response = await axios.get(`http://localhost:8000/api/stops/?stop_id=${stop_id}`);
        const fetchedStopData = response.data;
        setSelectedStop(fetchedStopData.stops_data[0]);
        setRouteData(fetchedStopData.routes);
      }
    };

    fetchStopDetails();
  }, [stop_id]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNewSearch(event.target.value);
  };

  const filteredStops = data?.stops_data.filter((stop: StopData) =>{
    
    const stopNameWithoutDots = stop.stop_name.toLowerCase().replace('.', '');

    const searchQueryWithoutDots = newSearch.toLowerCase().replace('.', '');

    return stopNameWithoutDots.includes(searchQueryWithoutDots);
  });

  const handleStopClick = async (stop: StopData) => {
    setSelectedStop(stop);
    setNewSearch('');

    const response = await axios.get(`http://localhost:8000/api/stops/?stop_id=${stop.stop_id}`);
    const fetchedRouteIds = response.data.routes;

    setRouteData(fetchedRouteIds);
    router.push(`stops/?stop_id=${stop.stop_id}`);
  };

  const SmallMap = ({ lat, lon }: { lat: number; lon: number }) => {
    const mapRef = useSmallMap(lon, lat);

    return <div className={styles['map-container']} ref={mapRef} />;
  };

  if (isLoading) return <p>Ładowanie...</p>;
  if (isError) return <p>Błąd podczas ładowania danych</p>;
  if (!data) return <p>Nie znaleziono takiego przystanku</p>;

  return (
    <>
      <ButtonAppBar />
      <div className={styles['digital-clock']}>
        <DigitalClock />
      </div>
      <div className={styles['main-container']}>
        <div className={styles["search-container"]}>
          <input
            placeholder="Nazwa przystanku"
            value={newSearch}
            onChange={handleInputChange}
          />
          <button>Szukaj</button>
        </div>

        <div className={styles['hint-container']}>
          {newSearch.length >= 2 && (
            <ul className={styles['ul-search']}>
              {filteredStops?.map(stop => (
                <li key={stop.stop_id} onClick={() => handleStopClick(stop)}>
                  {stop.stop_name}
                </li>
              ))}
            </ul>
          )}
        </div>  
      </div>
      <div className={styles['selected-stop-container']}>
        {selectedStop && (
          <div>
            <div className={styles['selected-stop-message']}>
              <div className={styles['route-button-grid']}>
                {routeData?.map((route) => (
                  <button className={styles['route-id-button']} key={route.route_id}>
                    <Link href={`/route/${route.route_id}/stop/${selectedStop.stop_id}/direction/${route.direction_id}`}>
                      {`${route.route_id}`}
                    </Link>
                  </button>
                ))}
              </div>
              <p>Skrót nazwy: {selectedStop.stop_code}</p>
              <p>Nazwa przystanku: {selectedStop.stop_name}</p>
              <p>Strefa: {selectedStop.zone_id}</p>
            </div>
            <div className={styles['small-map-container']}>
              <SmallMap
                lat={parseFloat(selectedStop?.stop_lat || "0")}
                lon={parseFloat(selectedStop?.stop_lon || "0")}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default StopSearch;
