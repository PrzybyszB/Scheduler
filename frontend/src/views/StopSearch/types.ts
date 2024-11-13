
export type StopData = {
  stop_id: string;
  stop_code: string;
  stop_name: string;
  stop_lat: string;
  stop_lon: string;
  zone_id: string;
};


export type RouteData = {
  route_id: string;
  direction_id: string;
};


export type ResponseStopsData = {
  stops_data: StopData[];
  routes: RouteData[];
};