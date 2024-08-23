import React from 'react';
import styles from './styles.module.scss';


const AppBar = () =>{
  return(
    <>
        <div className={styles['button-container']}>
          <button className={styles['button']} >Shop</button>
          <button className={styles['button']} >Login</button>
          <button className={styles['button']} >Register</button>
        </div>
      
    </>
      
    )
}

export default AppBar;