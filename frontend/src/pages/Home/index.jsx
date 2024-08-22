import React, { useState } from 'react';
import ButtonAppBar from '/src/components/Appbar/Appbar.jsx';
import TramBusButton from "/src/pages/Home/Components/Buttons/MainButtons.jsx";
import DigitalClock from '/src/pages/Home/Components//Digitalclock/Digitalclock.jsx';
import DigitalClock2 from '/src/pages/Home/Components//Digitalclock/Digitalclock2.jsx';
import '/src/styles/home.css';
import MapComponent from '/src/pages/Home/Components/Map/MapComponent.jsx';


export default function Home() {
    const [isFaded, setIsFaded] = useState(false);

    const handleZoomChange = (zoom) => {
        setIsFaded(zoom > 13); 
    };



    return (
        <div className="home-container">
            {/* <MapComponent onZoomChange={handleZoomChange} /> */}
            <div className={`app-bar${isFaded ? 'faded' : ''}`}>
                <ButtonAppBar />
            </div>
            <div className={`digital-clock${isFaded ? 'faded' : ''}`}>
                <DigitalClock />
                <DigitalClock2/>
            </div>
            <div className={`tram-bus-buttons${isFaded ? 'faded' : ''}`}>
                <TramBusButton />
            </div>
        </div>
    );
}