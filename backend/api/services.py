# #  Idea is a make separate py with logic with redis database



# from .tasks import client
# from rest_framework.response import Response
# import json



#     stop_times_key = 'stop_times.txt'
#     trips_key = 'trips.txt'
#     stops_key = 'stops.txt'
        
#     try:
#         stop_times_data = client.get(stop_times_key)
#         trips_data = client.get(trips_key)
#         stops_data = client.get(stops_key)
#     except (ConnectionError, TimeoutError) as e:
#         print({'error': 'Error retrieving data from the client.'}, status=500)

#     try:
#         stop_times_json_data = json.loads(stop_times_data)
#         trips_json_data = json.loads(trips_data)
#         stops_json_data = json.loads(stops_data)
#     except json.JSONDecodeError as e:
#         print({'error': 'Error decoding JSON data.'}, status=500)



# def stops():

#     for stops in stops_json_data:
#         stop_id = stops['stop_id']
#         stop_name = stops['stop_name']
    
