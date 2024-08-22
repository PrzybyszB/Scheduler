import   { useState, useEffect } from 'react'; 
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/apiClient/client';
import axios from 'axios';

type ResponseRouteData = {
    route_id: number;
    route_short_name: string;
    route_long_name: string;
    route_desc: string;
    route_type: number;
    route_color: string;
    route_text_color: string;
};

const fetchRouteData = async (): Promise<ResponseRouteData> => {
    const response = await axios.get('/api/test-16');
 
    return response.data;
};

function Route16({...props}) { 
    console.log(props)
    const {data} = useQuery({
        queryKey: ['test'],
        queryFn: fetchRouteData,
    })
    console.log(data)
 
 
    if(!data) {
        return <p>No data found</p>
    }

    return (
        <div>
         
                    <h1>Route ID: {data.route_id}</h1>
                    <p>Short Name: {data.route_short_name}</p>
                    <p>Long Name: {data.route_long_name}</p>
                    <p>Description: {data.route_desc}</p>
                    <p>Type: {data.route_type}</p>
                    <p>Color: #{data.route_color}</p>
                    <p>Text Color: #{data.route_text_color}</p>
           
       
        </div>
    );
}

export default Route16;