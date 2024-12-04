export type ResponseStopsData = {
  stops_data:
  [{
    stop_id: string,
    stop_code: string,
    stop_name: string,
    stop_lat: string,
    stop_lon: string,
    zone_id: string
  }
  ],
  route_id: {
    route_id: [string]
  }
};