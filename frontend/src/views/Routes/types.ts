export type ResponseRouteData = {
    route_id: string;
    most_popular_patterns: {
        [direction_id: string]: {
            stops: {
                stop_name: string;
                stop_id: string;
            }[];
            trip_headsign: string;
        };
    };
};
