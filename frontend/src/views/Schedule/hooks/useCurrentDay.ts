import { useState, useEffect } from 'react';

const useCurrentDay = (): [string, (day: string) => void] => {
    
  const [selectedDay, setSelectedDay] = useState<string>('');

  // Set the current day on load
  useEffect(() => {
    const today = new Date();
    const day = today.toLocaleString('en-US', { weekday: 'long' }).toLowerCase();
    setSelectedDay(day);
  }, []);

  return [selectedDay, setSelectedDay];
};

export default useCurrentDay;