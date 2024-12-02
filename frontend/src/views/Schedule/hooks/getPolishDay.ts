const useGetPolishDay = (day: string): string => {
    const daysMap: { [key: string]: string } = {
        'monday': 'Poniedziałek',
        'tuesday': 'Wtorek',
        'wednesday': 'Środa',
        'thursday': 'Czwartek',
        'friday': 'Piątek',
        'saturday': 'Sobota',
        'sunday': 'Niedziela'
    };
    return daysMap[day] || day;
};

export default useGetPolishDay;