import redis
import requests
import sys
import json
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson


client = redis.Redis(host='localhost', port=6379, db=0)

URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'

def fetch_and_convert_pb_to_json(url, key):
    response = requests.get(url)
    response.raise_for_status()

    # Create feed message object
    feed = gtfs_realtime_pb2.FeedMessage()
    
    # Parsing HTTP response content into object FeedMessage
    feed.ParseFromString(response.content)
    
    # Convert protobuf object into JSON format(but its string)
    json_data_format = MessageToJson(feed)

    # Saving file into Redis with unique key
    client.set(key, json_data_format)

    return json_data_format



trip_updates_data = fetch_and_convert_pb_to_json(URL_RT_1, 'trip_updates')
feeds_data = fetch_and_convert_pb_to_json(URL_RT_2, 'feeds')
vehicle_positions_data = fetch_and_convert_pb_to_json(URL_RT_3, 'vehicle_positions')

# Loading Redis files as JSON file
trip_updates_json = json.loads(trip_updates_data)
feeds_json = json.loads(feeds_data)
vehicle_positions_json = json.loads(vehicle_positions_data)


print(trip_updates_json['header']['timestamp'])

'''
if __name__ == '__main__':
    delay = sys.argv[1]

    while True:
        # Pobieram z url dane

        # Sprawdzam czy to są te same dane, jeśli tak to skipuje reszte

        # Obrabiam je w format dla REDIS

        # Wysyłam do REDISA

        # Czekam na kolejną iteracje

        # next celery i taskque
        sleep(delay)


'''