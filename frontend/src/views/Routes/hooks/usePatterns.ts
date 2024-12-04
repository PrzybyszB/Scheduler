import useFetchRouteDetail from "./useFetchRoute";

const usePatterns = (route_id: string) => {
    const { data, isError, isLoading } = useFetchRouteDetail(route_id);

    const patterns = data
        ? Object.entries(data.most_popular_patterns).map(([direction_id, { stops }]) => ({
            direction_id,
            stops,
        }))
        : [];

    return { patterns, isError, isLoading };
};

export default usePatterns;