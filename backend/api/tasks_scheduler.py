# Work in progress

'''
from django_q.tasks import async_task, async_chain, schedule
from api.tasks import check_and_fetch_RT_file, check_and_fetch_static_file, load_agency, load_calendar, load_feed_info, load_routes, load_shapes, load_stop_times, load_stops, load_trips


URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'
URL_STATIC_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGTFSFile'



def start_task():
    async_task(check_and_fetch_RT_file, url=URL_RT_1, key='trip_updates')
    async_task(check_and_fetch_RT_file, URL_RT_2, 'feeds')
    async_task(check_and_fetch_RT_file, URL_RT_3, 'vehicle_positions')

    schedule(
        func='api.tasks.check_and_fetch_RT_file',
        args=[URL_RT_1, 'trip_updates'],
        schedule_type='I',
        seconds= 50000,
        repeats= -1
    )
    schedule(
        func='api.tasks.check_and_fetch_RT_file',
        args=[URL_RT_2, 'feeds'],
        schedule_type='I',
        seconds= 500000,
        repeats= -1
    )
    schedule(
        func='api.tasks.check_and_fetch_RT_file',
        args=[URL_RT_3, 'vehicle_positions'],
        schedule_type='I',
        seconds= 500000,
        repeats= -1
    )

    async_task(check_and_fetch_static_file, URL_STATIC_1, 'gtfs_static')
    async_task(load_agency)
    async_task(load_stops)
    async_task(load_routes)
    async_task(load_shapes)
    async_task(load_calendar)
    async_task(load_feed_info)
    async_task(load_trips)
    async_task(load_stop_times)

    schedule(
        func='api.tasks.check_and_fetch_static_file',
        args=[URL_STATIC_1, 'gtfs_static'],
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_agency',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_stops',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_routes',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_shapes',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_calendar',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_feed_info',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_trips',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )

    schedule(
        func='api.tasks.load_stop_times',
        schedule_type='I',
        seconds= 4200,
        repeats= -1
    )


'''