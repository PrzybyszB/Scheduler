import React from 'react';
import 'ol/ol.css';
import useMap from '../../views/Map/hooks/useMap';
import styles from './styles.module.scss'

const MapComponent = () => {
    const mapRef = useMap();

    return (
        <div className={styles['map-container']}>
            <div className={styles['map-component']} ref={mapRef} />
        </div>
    );
};

export default MapComponent;
