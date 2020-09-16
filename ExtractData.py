import requests
import json
from pathlib import Path
import os
import pandas as pd

class Extract():

    data_sources = json.load(open('data_config.json'))
    json = data_sources['data_sources']['json']
    csv = data_sources['data_sources']['csv']
    authTwitter = data_sources['auth']['twitter']
    get_output = data_sources['output_files']['twitter']
    

    def getCsvData(self, csv_name):
        if os.path.isfile(self.csv[csv_name]):
            df = pd.read_csv(self.csv[csv_name])
            return df

        else:
            print(self.csv[csv_name], ' not exist!')

    def getJsonData(self, json_name):
        
        path = self.json[json_name]
        if os.path.isdir(path):
            return [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
        
        else:
            print(path, ' doesnt exist!')

    def getPath(self, file):
        return self.json[file]

    def getAuth(self):
        return [self.authTwitter['token'], 
                self.authTwitter['token_secret'],
                self.authTwitter['consumer_key'],
                self.authTwitter['consumer_secret']
                ]

    def get_tweet_imgs_path(self):
        return self.get_output['tweet_images']
    
    def get_profile_img_path(self):
        return self.get_output['profile_images']