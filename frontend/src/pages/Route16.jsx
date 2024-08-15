import React, { useState, useEffect } from 'react';
import api from "../api"; 

function Route16() {
    
    const [routeData, setRouteData] = useState(null);

    
    useEffect(() => {
        const fetchRouteData = async () => {
            const response = await api.get('/api/test-16/');
            
            setRouteData(response.data); 
        };
        
        fetchRouteData();
         
    }, []); 

    
    return (
        <div>
            {routeData ? (
                <div>
                    <h1>Route ID: {routeData.route_id}</h1>
                    <p>Short Name: {routeData.route_short_name}</p>
                    <p>Long Name: {routeData.route_long_name}</p>
                    <p>Description: {routeData.route_desc}</p>
                    <p>Type: {routeData.route_type}</p>
                    <p>Color: #{routeData.route_color}</p>
                    <p>Text Color: #{routeData.route_text_color}</p>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
}

export default Route16;