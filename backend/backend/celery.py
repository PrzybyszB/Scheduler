import os
from celery import Celery
from datetime import timedelta
from api.tasks import check_and_fetch_RT_file, check_and_fetch_static_file


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'
URL_STATIC_1 = 'https://www.ztm.poznan.pl/en/dla-deweloperow/getGTFSFile'


app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'check_and_fetch_RT_file_URL_RT_1': {
        'task': 'api.tasks.check_and_fetch_RT_file',
        'schedule': 50000.0,  # every 50000 sec
        'args': (URL_RT_1, 'trip_updates'),
    },
    'check_and_fetch_RT_file_URL_RT_2': {
        'task': 'api.tasks.check_and_fetch_RT_file',
        'schedule': 50000.0,  # every 50000 sec
        'args': (URL_RT_2, 'feeds'),
    },
    'check_and_fetch_RT_file_URL_RT_3': {
        'task': 'api.tasks.check_and_fetch_RT_file',
        'schedule': 50000.0,  # every 50000 sec
        'args': (URL_RT_3, 'vehicle_positions'),
    },
    'check_and_fetch_file_URL_STATIC_1': {
        'task': 'api.tasks.check_and_fetch_static_file',
        'schedule': 50000.0,  # every 50000 sec
        'args': (URL_STATIC_1, 'gtfs_static'),
    },
}

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

