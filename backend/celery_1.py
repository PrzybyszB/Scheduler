from celery import Celery
from datetime import timedelta
from backend.tasks_1 import check_file, fetch_and_convert_pb_to_json

app = Celery('tasks', broker='redis://0.0.0.0:6379/0', backend='redis://0.0.0.0:6379/0')

URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'


app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'check_file_URL_RT_1': {
        'task': 'tasks.check_file',
        'schedule': 15.0,  # every 15 sec
        'args': (URL_RT_1, 'trip_updates'),
    },
    'check_file_URL_RT_2': {
        'task': 'tasks.check_file',
        'schedule': 15.0,  # every 15 sec
        'args': (URL_RT_2, 'feeds'),
    },
    'check_file_URL_RT_3': {
        'task': 'tasks.check_file',
        'schedule': 15.0,  # every 15 sec
        'args': (URL_RT_3, 'vehicle_positions'),
    },
}

if __name__ == '__main__':
    app.start()