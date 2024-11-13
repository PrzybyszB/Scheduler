import React from 'react';
import useSmallMap from '../hooks/useSmallMap';
import styles from './styles.module.scss';

const SmallMap = ({ lat, lon }: { lat: number; lon: number }) => {
  const mapRef = useSmallMap(lon, lat);

  return <div className={styles['map-container']} ref={mapRef} />;
};

export default SmallMap;