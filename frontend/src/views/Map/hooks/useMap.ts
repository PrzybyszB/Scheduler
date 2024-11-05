import { useRef, useEffect } from 'react';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';




const useMap = () => {
    const mapRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (mapRef.current) {
            // Create map
            const initialCenter = fromLonLat([16.9252, 52.4064])
            const map = new Map({
                target: mapRef.current,
                layers: [
                    new TileLayer({
                        source: new OSM(),
                    }),
                
                ],
                view: new View({
                    // Converting lat long coordinate to EPSG:3857 (Center of Poznań)
                    center: initialCenter,
                    zoom: 13,
                    minZoom: 10,
                    maxZoom : 18,

                    // Define the extent around initial center
                    extent: [
                        initialCenter[0] - 20000, // Min X
                        initialCenter[1] - 20000, // Min Y
                        initialCenter[0] + 20000, // Min X
                        initialCenter[1] + 20000, // Min Y
                    ],
                }),
            });

            // Create unique hooks that will be listen zoom level for shading
            // const handleZoomChange = () =>{
            //     const zoom = map.getView().getZoom();
            //     if (onZoomChange){
            //         onZoomChange();
            //     }
            // };

            // map.getView().on('change:resolution', handleZoomChange);

            return () => {
                // Clearing map
                map.setTarget(undefined);
            };
        }
        },[]);

        return mapRef;

};

export default useMap;