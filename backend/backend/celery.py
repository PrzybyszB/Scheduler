import os
from celery import Celery, chain
from celery.signals import worker_ready
from api.tasks import check_and_fetch_RT_file, check_and_fetch_static_file, load_agency, load_stops, load_routes, load_shapes, load_calendar, load_feed_info, load_trips, load_stop_times, process_trip_detail, create_active_routes, save_schedules_to_redis, create_active_stop_id

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')


zip_file_path = 'backend/api/GTFS-ZTM/GTFS-ZTM-STATIC/20240907_20240930.zip'
URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'
URL_STATIC_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGTFSFile'




app.conf.broker_connection_retry_on_startup = True


app.conf.beat_schedule = {
    # 'check_and_fetch_RT_file_URL_RT_1': {
    #     'task': 'api.tasks.check_and_fetch_RT_file',
    #     'schedule': 50000000.0,  # every  50000000 sec
    #     'args': (URL_RT_1, 'trip_updates'),
    # },
    # 'check_and_fetch_RT_file_URL_RT_2': {
    #     'task': 'api.tasks.check_and_fetch_RT_file',
    #     'schedule':  50000000.0,  # every  50000000 sec
    #     'args': (URL_RT_2, 'feeds'),
    # },
    # 'check_and_fetch_RT_file_URL_RT_3': {
    #     'task': 'api.tasks.check_and_fetch_RT_file',
    #     'schedule':  50000000.0,  # every  50000000 sec
    #     'args': (URL_RT_3, 'vehicle_positions'),
    # },
    # 'check_and_fetch_file_URL_STATIC_1': {
    #     'task': 'api.tasks.check_and_fetch_static_file',
    #     'schedule':  86400.0,  # every  86400 sec
    #     'args': (URL_STATIC_1, 'gtfs_static'),
    # },
    'execute_daily_chain' : {
    'task': 'backend.tasks.execute_daily_chain',
    'schedule': 86400.0,  # every 24h
    },

}

@app.task
def conditional_chain_check(result, *args, **kwargs):
    '''
    It triggers the rest of the chain if the first task returns True
    '''
    if result:
        chain(
            create_active_routes.si(),
            create_active_stop_id.si(),
            process_trip_detail.si(),
            save_schedules_to_redis.si(),
            load_agency.si(),
            load_stops.si(),
            load_routes.si(),
            load_shapes.si(),
            load_calendar.si(),
            load_feed_info.si(),
            load_trips.si(),
            load_stop_times.si()
        ).apply_async()
    else:
        print("Static file is up to date. Skip rest of tasks.")


@worker_ready.connect
def load_tasks_on_startup(**kwargs):
    '''
    .delay() - async and automatic executes a task in the background
    .s() - signature, allows passing arguments to the task and scheduling its execution
    .si() - Like .s(), but ignores the result of the previous task in the chain, which enables precise control of the arguments.
    .apply_async() - its delay() with more options, better usage for chain
    '''

    # Load task on startup
    check_and_fetch_RT_file.delay(URL_RT_1, 'trip_updates'),
    check_and_fetch_RT_file.delay(URL_RT_2, 'feeds'),
    check_and_fetch_RT_file.delay(URL_RT_3, 'vehicle_positions')
    
    chain(
        check_and_fetch_static_file.si(URL_STATIC_1, 'gtfs_static'),
        conditional_chain_check.s()
    ).apply_async()


@app.task
def execute_daily_chain():
    chain(
        check_and_fetch_static_file.si(URL_STATIC_1, 'gtfs_static'),
        conditional_chain_check.s()
    ).apply_async()

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

