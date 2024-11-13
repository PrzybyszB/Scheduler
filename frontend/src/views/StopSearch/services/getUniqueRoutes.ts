import { RouteData } from "../types";

const getUniqueRoutes = (routeData: RouteData[]): RouteData[] => {
  if (!routeData || routeData.length < 3) {
    return routeData;
  }

  const uniqRouteDataObject = routeData.reduce((acc, route) => {
    if (!acc[route.route_id]) {
      acc[route.route_id] = route;
    }
    return acc;
  }, {} as { [key: string]: RouteData });

  return Object.values(uniqRouteDataObject);
};

export default getUniqueRoutes;