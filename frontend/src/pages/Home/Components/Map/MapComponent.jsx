import React from 'react';
import 'ol/ol.css';
import useMap from '/src/pages/Home/Components/Map/Hooks/useMap.jsx';

const MapComponent = ({ onZoomChange }) => {
    const mapRef = useMap(onZoomChange);

    return <div className='map-component'
                ref={mapRef} 
                style={{ width: '100%', height: '100%' }}></div>;
};

export default MapComponent;
