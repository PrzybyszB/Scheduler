export type ResponseScheduleData = {
    current_day: string;
    schedules: Array<{
        route_id: string;
        departure_time: string;
        stop_id: string;
        start_date: string;
        direction_id: string;
    }>;
    stop_name: string;
    stop_headsign: string;
};