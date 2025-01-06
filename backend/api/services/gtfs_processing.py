import tempfile
import os
import gtfs_kit as gk
import redis
import csv
import re
import zipfile
import io
import requests
from datetime import datetime
from io import StringIO
from redis.exceptions import RedisError
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson


class GTFSService:
    '''
    Class create to handle processing gtfs data and redis data
    '''

    def __init__(self):
        self.client = redis.StrictRedis(host='redis', port=6379, db=0)

    def fetch_gtfs_files_from_redis(self):
        '''
        Fetches all keys from Redis, filters out keys ending with ':hash', decodes them to strings, and returns the list of remaining keys.
        '''
        try:
            all_keys = self.client.keys('*')
            gtfs_keys = []
            
            for key in all_keys:
                decoded_key = key.decode('utf-8')
                
                if not decoded_key.endswith(':hash'):
                    gtfs_keys.append(decoded_key)

            return gtfs_keys
        
        except Exception as e:
            return {'error': 'There was an error ' + str(e)}
    
    def fetch_data_from_redis(self, keys):
        '''
        Fetch data from redis and decode it 
        '''
        fetch_data = {}
        try:
            for key in keys:
                data = self.client.get(key).decode('utf-8')
                fetch_data[key] = data
            return fetch_data
        except (ConnectionError, TimeoutError) as e:
            raise Exception(f"Error retrieving data from Redis: {e}")
         
    def parse_csv_data(self, data):
        '''
        Parse CSV data into Dict Reader objects
        '''
        csv_data = {}

        for key, value in data.items():
            csv_data[key] = csv.DictReader(StringIO(value))
        return csv_data

    def load_gtfs_feed_from_redis(self,filename):
        '''
        Use a temporary file to handle the GTFS data using gtfskit
        '''

        try:
            file_content = self.client.get(filename)
            if file_content:

                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:

                    # Load GTFS data from the temporary file
                    feed = gk.feed.read_feed(path_or_url=temp_file_path, dist_units='km')
                    return feed
                except Exception as e:
                    return {'error': f'Error loading GTFS feed from {temp_file_path}: {e}'}
                finally:

                    # Remove the temporary file
                    os.remove(temp_file_path)
            else:
                return {'error': f'File {filename} not found in Redis.'}
        except Exception as e:
            return {'error': f'Error loading GTFS feed from Redis: {e}'}

    def extract_date_from_filename(self, filename):
        '''
        Extract date from the filename (e.g., '20240907_20240930.zip')
        '''
        try:
            date_str = filename.split('_')[0]

            # Convert string to date object
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:

            # If the date format is invalid, skip this file
            return None    
        
    def get_active_route_ids(self):
        '''
        Fetch all active route_ids from Redis set 'active:route_ids'
        '''
        try:
            return self.client.smembers("active:route_ids")
        except Exception as e:
           return {'error': f'Error loading active route_ids from Redis: {e}'}
    
    def get_active_stop_ids(self):
        '''
        Fetch all active stop_ids from Redis set 'active:stop_ids'
        '''
        try:
            return self.client.smembers("active:stop_ids")
        except Exception as e:
            return {'error': f'Error loading active stop_ids from Redis: {e}'}
        
    def get_active_stop_names(self, stop_id):
        '''
        Fetch the name of a stop based on its stop_id from the Redis hash 'active:stop_names'
        '''
        try:
            stop_name = self.client.hget("active:stop_names", stop_id)
            if stop_name:
                return stop_name.decode('utf-8')
            else:
                return {'error': f'Stop_id {stop_id} not found in Redis'}
        except Exception as e:
            return {'error': f'Error fetching stop_name from Redis: {e}'}

    def convert_time_format(self, time_str):
        """
        Converts time strings in 'HH:MM:SS' format where HH can be >= 24 to a valid time.
        """
        hours, minutes, seconds = map(int, time_str.split(':'))
        if hours >= 24:
            hours -= 24
        return f'{hours:02}:{minutes:02}:{seconds:02}'
    
    def get_filename_from_content_disposition(self, content_dispositon):
        '''
        The zip file name represents the start and end dates for which the update is valid. It is important to name the files with these date ranges so that in the case of incomplete files, we can go back to the dates and complete them.
        '''
        
        # Extracts the filename from the Content-Disposition header.
        if content_dispositon is None:
            return None
        
        # Use a regular expression to find the filename within the Content-Disposition header
        # The pattern 'filename="(.+)"' looks for 'filename="something"' and captures 'something'
        filename = re.findall('filename="(.+)"', content_dispositon)
        if len(filename) == 0:
            return None
        
        # Return the first match found in the Content-Disposition header
        return filename[0]

    def process_file(self, file_content, zip_name):

        with zipfile.ZipFile(io.BytesIO(file_content)) as z:
            for file_name in z.namelist():

                with z.open(file_name) as f:
                    file_content = f.read()

                    # Deleting Byte Order Mark
                    file_content = file_content.lstrip(b'\xef\xbb\xbf')
                    
                    decoded_file = file_content.decode('utf-8')
                    
                    ttl_in_seconds = 15 * 24 * 3600
                    self.client.setex(file_name, ttl_in_seconds, decoded_file)
                        
                    print(f'File {file_name} stored')

    def fetch_and_convert_pb_to_json(self, url, key):
        '''
        Fetching and converting protobuff files to json and saving to redis
        '''

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
            self.client.setex(key, ttl_in_seconds, json_data_format)
            
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