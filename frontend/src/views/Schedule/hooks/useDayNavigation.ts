import { useRouter } from 'next/router';

const useDayNavigation = (route_id: string | string[], stop_id: string | string[], direction_id: string | string[], setSelectedDay: (day: string) => void) => {
  const router = useRouter();

  const handleDayClick = (day: string) => {
    setSelectedDay(day);
    router.push(`/route/${route_id}/stop/${stop_id}/direction/${direction_id}?day=${day}`);
  };

  return handleDayClick;
};

export default useDayNavigation;