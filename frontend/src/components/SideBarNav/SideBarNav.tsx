import React from 'react';
import Link from 'next/link';
import styles from './styles.module.scss';
import cx from 'classnames'


interface Image {
  url: string;
  title: string;
  link: string;
}

const images: Image[] = [
  {
    url: '/Tram.png',
    title: 'Tram',
    link: '/tram-list',
  },
  {
    url: '/Bus.png',
    title: 'Bus',
    link: '/bus-list',
  },
  {
    url: '/Busstop.png',
    title: 'Stops',
    link: '/stops',
  },
  {
    url: '/Map.png',
    title: 'Map',
    link: '/map',
  },
];


type Props = {
  theme?: 'tram-nav-side-bar' | 'bus-nav-side-bar' | 'routes-nav-side-bar' | 'stop-nav-side-bar'
}

const SideBarNav = ({theme}: Props) => {
  return (
    <div className={cx(styles['container'], styles[`container-${theme}`])}>
      {images.map((image) => (
        <Link className={styles['image-button']}
          key={image.title} 
          href={image.link} 
          passHref>
            <span
              className={styles['image-src']}
              style={{ backgroundImage: `url(${image.url})` }}/>
            <span className={styles['image-backdrop']} />
            <span className={styles['image']}>
              <span className={styles['typography']}>
              </span>
            </span>
        </Link> 
      ))}
    </div>
  );
}


export default SideBarNav ;