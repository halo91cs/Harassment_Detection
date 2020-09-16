from Transformation import Transformation
from ExtractData import Extract
import pandas as pd
import urllib
import os
import demoji
import twitter
import json
import numpy as np
import time

class ExtractImages():
    transObj = Transformation()   
    extractObj = Extract()
    twitter = extractObj.getAuth()   
    
    # Download profile images based on users' ids through twitter api.
    def download_profile_images(self):
        df = self.transObj.aggregated_dataset()
        
        t = twitter.Twitter(auth=twitter.OAuth(self.twitter[0], self.twitter[1], self.twitter[2], self.twitter[3]))
        # since we have 722 interactions, it makes sense to divide the df into 6 and wait for 15 sec. for each batch.
        # When Sending too many requests to twitter, it blocks to download.. 
        # That's why we wait for 15 sec for each batch and continue..
        splitted = np.array_split(df, 6) 
        for j in splitted:
            
            for i in j.itertuples():
                
                try: 
                    info = t.users.lookup(user_id=(getattr(i, 'Source_user_id')))
                    profImg = info[0]["profile_image_url_https"]
                    ext = (os.path.splitext(profImg)[1]).split('.')[1]
                    imgName = (getattr(i, 'Source') + '.' + ext)
                    urllib.request.urlretrieve(profImg, "~/output/profile_images/%s" % imgName)
                
                except:
                    print('No user found!')
        
            time.sleep(15)    

    def download_tweet_images(self):

        df = self.transObj.create_dataset()
        for i in df.itertuples():
            for j in getattr(i, 'Media_type'):        
                # if media type is photo. (we are only interested in images)
                # this part can be modified to obtain videos as well.
                if j == 'photo':

                    media_url = getattr(i, 'Media_url_https')[0]
                    ext = (os.path.splitext(media_url)[1]).split('.')[1]
                    imgName = (getattr(i, 'Source') + '.' + getattr(i, 'Target') + '.' + str(getattr(i, 'row_id')) + '.' + ext)

                    try:
                        urllib.request.urlretrieve(media_url, "~/output/tweet_images/%s" % imgName)
                    except:
                        pass        
    
