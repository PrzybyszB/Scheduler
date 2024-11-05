import { useRef, useEffect } from 'react';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';
import { Feature } from 'ol';
import { Point } from 'ol/geom';
import { Style, Icon } from 'ol/style';
import { Vector as VectorLayer } from 'ol/layer';
import VectorSource from 'ol/source/Vector';

const useSmallMap = (stop_lon: number, stop_lat: number) => {
    const mapRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (mapRef.current) {
            const initialCenter = fromLonLat([stop_lon, stop_lat]);

            // Tworzenie mapy
            const map = new Map({
                target: mapRef.current,
                layers: [
                    new TileLayer({
                        source: new OSM(),
                    }),
                ],
                view: new View({
                    center: initialCenter,
                    zoom: 17,
                    minZoom: 15,
                    maxZoom: 18,
                    extent: [
                        initialCenter[0] - 500,
                        initialCenter[1] - 500,
                        initialCenter[0] + 500,
                        initialCenter[1] + 500,
                    ],
                }),
            });

            
            const iconFeature = new Feature({
                geometry: new Point(fromLonLat([stop_lon, stop_lat])),
            });

            const iconStyle = new Style({
                image: new Icon({
                    anchor: [0.5, 0.8], 
                    src: '/red_pointer.png', 
                    scale: 0.1, 
                }),
            });

            iconFeature.setStyle(iconStyle);

            const vectorSource = new VectorSource({
                features: [iconFeature],
            });

            const vectorLayer = new VectorLayer({
                source: vectorSource,
            });

            map.addLayer(vectorLayer);

            return () => {
                map.setTarget(undefined);
            };
        }
    }, [stop_lon, stop_lat]);

    return mapRef;
};

export default useSmallMap;
