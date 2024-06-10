from google.transit import gtfs_realtime_pb2
import requests


# https://developers.google.com/transit/gtfs-realtime?hl=pl
# https://github.com/MobilityData/gtfs-realtime-bindings/blob/master/python/README.md
# gtfs.org

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb')
feed.ParseFromString(response.content)
for entity in feed.entity:
  if entity.HasField('trip_update'):
    print(entity.trip_update)



