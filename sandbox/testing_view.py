from backend.api.models import Route
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.api.serializers import RouteSerializer
from backend.api.tasks import client
import json
import logging
from rest_framework.response import Response
from django.http import HttpResponse

logger = logging.getLogger('api')

# path('api/test-16/', api_test_16, name='api_test_16'),
@api_view(['GET'])
def api_test_16(request):
    logger.info('Starting api test')
    route_16 = Route.objects.get(route_id=16)
    serializer_class = RouteSerializer(route_16)
    logger.debug('This is a debug message.')
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    return Response(serializer_class.data)

# path('16/RT', api_test_16_rt, name='api_test_16_rt'),
@api_view(['GET'])
def api_test_16_rt(request):
    trip_updates_key = 'trip_updates'
    feeds_key = 'feeds'
    vehicle_positions_key = 'vehicle_positions'

    trip_update_data = client.get(trip_updates_key)
    feeds_data = client.get(feeds_key)
    vehicle_positions_data = client.get(vehicle_positions_key)

    trip_update_json = json.loads(trip_update_data)
    feeds_json = json.loads(feeds_data)
    vehicle_positions_json = json.loads(vehicle_positions_data)

    positions = []


    for entity_vehicle in vehicle_positions_json['entity']:
        vehicle = entity_vehicle['vehicle']
        trip = vehicle['trip']
        route_id = trip['routeId']
        
        if route_id == "16":
            position = vehicle['position']
            positions.append(position)
            
            # for entity_trip in trip_update_json['entity']:
            #     trip_update = entity_trip['tripUpdate']
            #     trip = trip_update['trip']
            #     trip_route_id = trip['routeId']
                
            #     if trip_route_id == "16":
            #         stopTimeUpdate = trip_update['stopTimeUpdate']
            #         for stop_update in stopTimeUpdate:
            #             arrival = stop_update['arrival']
            #             delay = arrival['delay']
            #             if entity_vehicle['id'] == entity_trip['id']:
            #                 break
        
    return HttpResponse(f"Hello its me 16 tramwaj and my pozycja :Position: {positions}")


# path('RT', api_test_RT, name='api_test_RT'),
@api_view(['GET'])
def api_test_RT(request):
    keys = ['trip_updates', 'feeds', 'vehicle_positions']
    timestamps = []

    for key in keys:
        data = client.get(key)
        
        try:
            json_data = json.loads(data)
            timestamp = json_data['header']['timestamp']
            timestamps.append(timestamp)
        except KeyError:
            return HttpResponse(f'No timestamp found for key: {key}', 404)
        except json.JSONDecodeError as e:
            return HttpResponse(f'Error decoding JSON: {str(e)}', 500)
        
    return HttpResponse(', '.join(timestamps))

