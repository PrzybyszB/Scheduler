import tempfile
import os
import re
import gtfs_kit as gk
import redis
import pandas as pd
from datetime import datetime

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