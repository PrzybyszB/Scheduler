import requests
import redis
import json
import zipfile
import io
import hashlib
from google.protobuf.message import DecodeError
from redis.exceptions import RedisError
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson
from celery import Celery
from celery import shared_task


# app = Celery('tasks', broker='redis://0.0.0.0:6379/0', backend='redis://0.0.0.0:6379/0')

client = redis.Redis(host='redis')

URL_RT_1 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=trip_updates.pb'
URL_RT_2 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=feeds.pb'
URL_RT_3 = 'https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb'
URL_STATIC_1 = 'https://www.ztm.poznan.pl/en/dla-deweloperow/getGTFSFile'


@shared_task
def check_and_fetch_RT_file(url, key):
        
    try:
        response = requests.get(url)
        
        # Parsing new file from url
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        if feed.HasField('header'):
            header = feed.header
            new_file_timestamp = header.timestamp
        else:
            print("There is no header in new file")
            return
        
        print(f"New file timestamp for {key}: {new_file_timestamp}")

        # Looking for file in Redis db
        old_file = client.get(key)
        
        # Downlad if doesn't exist
        if old_file is None or old_file == b'':
            old_file = fetch_and_convert_pb_to_json(url, key)
            print(f"Downloaded file {key} to Redis")

        # Parsing data from Redis 
        json_data = json.loads(old_file)
        old_file_timestamp = int(json_data['header']['timestamp'])
        print(f"Old file timestamp for {key}: {old_file_timestamp}")

        if new_file_timestamp != old_file_timestamp:
             fetch_and_convert_pb_to_json(url, key)
        else:
            print(f"File {key} is up to date")
    
    except requests.exceptions.RequestException as e:
        print(f"Error while downloading file from URL: {e}")
    
    except DecodeError as e:
        print(f"Error while parsing file: {e}")
    
    except RedisError as e:
        print(f"Error while work with Redis: {e}")
    
    except json.JSONDecodeError as e:
        print(f"Error while parsing JSON: {e}")
    
    except KeyError as e:
        print(f"Key error while accessing JSON data: {e}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")

def fetch_and_convert_pb_to_json(url, key):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Create feed message object
        feed = gtfs_realtime_pb2.FeedMessage()
        
        # Parsing HTTP response content into object FeedMessage
        feed.ParseFromString(response.content)
        
        # Convert protobuf object into JSON format(but its string)
        json_data_format = MessageToJson(feed)

        # Saving file into Redis with unique key and setting time to live 
        ttl_in_seconds = 48 * 3600
        client.setex(key, ttl_in_seconds, json_data_format)
        
        print(f"File: {key} downloaded")
        
        return json_data_format
    
    
    except requests.exceptions.RequestException as e:
            print(f"Error while downloading file from URL: {e}")
    
    except DecodeError as e:
            print(f"Error while parsing file: {e}")
    
    except RedisError as e:
            print(f"Error while work with Redis: {e}")
    
    except Exception as e:
            print(f"Unexpected error: {e}")


@shared_task
def check_and_fetch_static_file(url, key):
    try:
        
        response = requests.get(url)
        response.raise_for_status()
        ttl_in_seconds = 7 * 24 * 3600

        # Checking hash of zip file to know if a new one needs to be downladed
        new_file_hash = hashlib.md5(response.content).hexdigest()
        stored_file_hash = client.get(f"{key}:hash")

        if not stored_file_hash:  
            process_file(response.content, key)
            client.setex(f"{key}:hash", ttl_in_seconds, new_file_hash)
            print(f"Downloaded file {key} and set new hash {new_file_hash}")
            return  

        print(f"Stored file hash is {stored_file_hash.decode('utf-8')}")

        if stored_file_hash.decode('utf-8') != new_file_hash:
            client.setex(f"{key}:hash", ttl_in_seconds, new_file_hash)
            process_file(response.content, key)
        else:
            print(f"Static ZIP file {key} is already up-to-date.")

    except requests.exceptions.RequestException as e:
        print(f"Error while downloading file from URL: {e}")

    except RedisError as e:
        print(f"Error while working with Redis: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

def convert_txt_to_json(txt_content):
    lines = txt_content.splitlines()
    header = lines[0].split(",")  
    json_data = []

    for line in lines[1:]:
        values = line.split(",")
        json_data.append(dict(zip(header, values)))

    return json_data

def process_file(file_content, key):
    with zipfile.ZipFile(io.BytesIO(file_content)) as z:
        for file_name in z.namelist():
            with z.open(file_name) as f:
                file_content = f.read()

                # Deleting Byte Order Mark
                file_content = file_content.lstrip(b'\xef\xbb\xbf')
                decoded_file = convert_txt_to_json(file_content.decode('utf-8')) 
                json_file = json.dumps(decoded_file)
                
                ttl_in_seconds = 7 * 24 * 3600
                client.setex(file_name, ttl_in_seconds, json_file)
                    
                print(f"File {file_name} stored as JSON")    

# # Check file
# trip_updates_data_check = check_and_fetch_RT_file(URL_RT_1, 'trip_updates')
# feeds_data_check = check_and_fetch_RT_file(URL_RT_2, 'feeds')
# vehicle_positions_data_check = check_and_fetch_RT_file(URL_RT_3, 'vehicle_positions')

# # Redis JSON format data
# trip_updates_data = fetch_and_convert_pb_to_json(URL_RT_1, 'trip_updates')
# feeds_data = fetch_and_convert_pb_to_json(URL_RT_2, 'feeds')
# vehicle_positions_data = fetch_and_convert_pb_to_json(URL_RT_3, 'vehicle_positions')

# # JSON data
# trip_updates_json = json.loads(trip_updates_data)
# feeds_json = json.loads(feeds_data)
# vehicle_positions_json = json.loads(vehicle_positions_data)
