import { useRef, useEffect } from 'react';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';

const useMap = (onZoomChange) => {
    const mapRef= useRef(null);

    useEffect(() => {
        if (mapRef.current) {
            // Create map
            const map = new Map({
                target: mapRef.current,
                layers: [
                    new TileLayer({
                        source: new OSM(),
                    }),
                
                ],
                view: new View({
                    // Converting lat long coordinate to EPSG:3857 (Center of Poznań)
                    center: fromLonLat([16.9252, 52.4064]),
                    zoom: 13,
                    minZoom: 13,
                    maxZoom : 18,
                }),
            });
            // Create unique hooks that will be listen zoom level for shading
            const handleZoomChange = () =>{
                const zoom = map.getView().getZoom();
                if (onZoomChange){
                    onZoomChange(zoom);
                }
            };

            map.getView().on('change:resolution', handleZoomChange);

            return () => {
                // Clearing map
                map.setTarget(null);
            };
        }
        },[onZoomChange]);

        return mapRef;

};

export default useMap;