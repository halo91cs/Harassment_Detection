from ExtractData import Extract
from RegexConfig import Configuration
from ImageProcessing import ImageProcessing
import pandas as pd
import json
import re
import demoji

class Transformation():
    extractObj = Extract()
    config = Configuration()
    img_process = ImageProcessing()
    lexicon = extractObj.getCsvData('harassment_lexicon') # data frame
    tweets_json = extractObj.getJsonData('tweets_json')
    path_to_tweets = extractObj.getPath('tweets_json')
    twitterAuth = extractObj.getAuth()
    img_path = extractObj.get_tweet_imgs_path()
    
    #def __init__(self):
    #    pass

    def processHarassmentLexicon(self):
        # combine columns in a list
        lex = [self.lexicon[i].dropna().tolist() for i in self.lexicon.columns.values.tolist()]
        
        # flatten the list of lists
        lex = [val for sub_lexicon in lex for val in sub_lexicon]
        
        # convert upper cases into lower case
        lex = [x.lower() for x in lex] 
        
        # remove duplicates from lexicon
        lex = self.config.removeListDuplicates(lex) #list(dict.fromkeys(lex))
        
        return lex

    # Returns a dictionary where each key is the source of the tweet and 
    # each value is the collection of tweet objects that are belonged to corresponding user
    # 469786 total tweets
    # 15293 tweets contain toxic words
    # 384 students' tweets will be considered, other ones had no tweet. or there was no toxic tweet
    def processTweets(self, lex):
        source_and_tweets = {}

        for i in self.tweets_json:
            ## Json files in tweets folder are named as follows: sourceName_tweets.json --> i 
            ## So we use the following re.sub to get the source of the tweet.
            source = self.config.stringReplace(i, '_tweets.json', '')#re.sub('\_tweets.json$', '', i) 

            line_generator = open(self.path_to_tweets + '/' + i)
  
            # ind_objects will store all tweet objects for each user that have harassing keyword in it.
            ind_objects = []

            for line in line_generator: ## line_generator has all tweet objects for a specific person..
                line_object = json.loads(line)

                if 'retweeted_status' in line_object.keys():
                
                # full_text attribute gives the tweet of the user.
                # if tweet is retweeted and tweet exceeds its length limit, then it is truncated,
                # So we check retweeted_status['full_text'] field to get the full tweet.
                    tweet = 'RT' + ' @' + line_object['retweeted_status']['user']['screen_name'] + ': ' + line_object['retweeted_status']['full_text']
                    
                else:
                    tweet = line_object['full_text']
                
                words = self.config.splitLowerText(tweet) #tweet.lower().split() # we get all the words in every sentence
                words = self.config.removeListDuplicates(words) #words = list(dict.fromkeys(words)) # we removed all the duplicates from the word list
                
                if any(item in lex for item in words):
                    ind_objects.append(line_object)

            source_and_tweets[source] = ind_objects     
            source_and_tweets = self.config.removeEmptyItemsDict(source_and_tweets)  ## after removing empty users, we get 382 total users in total.
            #source_and_tweets = {k: v for k, v in source_and_tweets.items() if v != []} 
        
        return source_and_tweets

    # This method checks if there is any url in a tweet object excluding media
    def check_url(self, tweet_object):
    
        url = []        
        # if tweet is retweeted
        if self.is_retweeted(tweet_object):
            
            # if there is a url in retweeted tweet.
            if tweet_object['retweeted_status']['entities']['urls'] != []:                
                for i in tweet_object['retweeted_status']['entities']['urls']:                
                    url.append(i['url'])
            else:
                url.append(None)
        else: # if tweet is not retweeted
            
            if tweet_object['entities']['urls'] != []:                
                for i in tweet_object['entities']['urls']:
                    url.append(i['url'])
            else:
                url.append(None)            
                
        return url
    
    # Check if tweet object is quoted
    def is_quoted(self, tweet_object):
    
        if tweet_object['is_quote_status'] == True:
            return True
        else:
            return False

    # Check if tweet object is retweeted
    def is_retweeted(self, tweet_object):
    
        if 'retweeted_status' in tweet_object.keys():
            return True
        else:
            return False

    # returns id of the user tweet object belongs to
    def get_user_id(self, tweet_object):        
        return tweet_object['user']['id_str']    

    # returns the url to pp of the sender of a tweet
    def get_user_pp(self, tweet_object):
        return tweet_object['user']['profile_image_url_https']

    # returns the quoted user's screen name
    def get_quoted_user(self, tweet_object):
        if self.is_quoted(tweet_object):            
            if self.is_retweeted(tweet_object):
                
                try:
                    return tweet_object['retweeted_status']['quoted_status']['user']['screen_name']
                except:
                    return None
            
            else:   
                try:
                    return tweet_object['quoted_status']['user']['screen_name']
                except:
                    return None            
        else:
            return None

    # Checks if there is any photo, video, etc. attached to tweet..
    def check_media(self, tweet_object):
        
        def get_media_info(k):
            
            media_url.append(k['url'])
            media_type.append(k['type'])
            if k['type'] == 'photo':
                media_url_https.append(k['media_url_https'])
            elif k['type'] == 'video':
                media_url_https.append(k['video_info']['variants'][1]['url'])
            elif k['type'] == 'animated_gif':
                media_url_https.append('animated_gif')
            else:
                media_url_https.append('None')
            
        media_url = []
        media_url_https = []
        media_type = []
        
        # Firstly check if there is a media
        if 'media' in tweet_object['entities'].keys() and not self.is_retweeted(tweet_object) and not self.is_quoted(tweet_object):
        
            for k in tweet_object['extended_entities']['media']:
                get_media_info(k)            
        
        # retweeted but not quoted
        if self.is_retweeted(tweet_object) and not self.is_quoted(tweet_object):
            
            if 'media' in tweet_object['retweeted_status']['entities'].keys():
                
                for k in tweet_object['retweeted_status']['extended_entities']['media']:
                    get_media_info(k)
        
        # not retweeted but quoted
        if not self.is_retweeted(tweet_object) and 'quoted_status' in tweet_object.keys():
            
            if 'media' in tweet_object['quoted_status']['entities'].keys():
                
                for k in tweet_object['quoted_status']['extended_entities']['media']:
                    get_media_info(k)
        
        # no media, no retweet, no quoted
        if 'media' not in tweet_object['entities'].keys() and not self.is_retweeted(tweet_object) and not self.is_quoted(tweet_object):
            
            media_url.append(None)
            media_type.append(None)
            media_url_https.append(None)
    
        return [media_url, media_url_https, media_type]

    def extract_emojis(self, df):

        return list(df.apply(lambda row: demoji.findall(row['Tweet']), axis=1))

    

    def create_dataset(self):

        dct = self.processTweets(self.processHarassmentLexicon())
                
        def fill_df_fields(target_all, k, tweet_object):
            sources.append(tweet_object['user']['screen_name'])
            
            if target_all != []:            
                targets.append(k)
            else:
                targets.append('None')

            if self.is_retweeted(tweet_object):
                tweet = 'RT' + ' @' + tweet_object['retweeted_status']['user']['screen_name'] + ': ' + tweet_object['retweeted_status']['full_text']
                tweets.append(tweet)
            else:
                tweets.append(tweet_object['full_text'])
                
            created_at.append(tweet_object['created_at'])
            favorite_count.append(tweet_object['favorite_count'])
            media_url_https_all.append(self.check_media(tweet_object)[1])
            media_type_all.append(self.check_media(tweet_object)[2])
            media_url_all.append(self.check_media(tweet_object)[0])
            is_retweeted_all.append(self.is_retweeted(tweet_object))
            normal_url_all.append(self.check_url(tweet_object))
            is_quoted_all.append(self.is_quoted(tweet_object))
            source_user_id.append(self.get_user_id(tweet_object))
        
        df = pd.DataFrame()
        sources = []
        targets = []
        tweets = []
        created_at = []
        favorite_count = []
        media_url_https_all = []
        media_type_all = []
        media_url_all = []
        normal_url_all = []
        is_retweeted_all = []
        is_quoted_all = []
        source_user_id = []
        for i in dct.items():
            #print(i[0])
            ## type of i is a tuple where i[0] is the source of the tweet and i[1] is the all tweets of corresponding source

            for j in i[1]: ## iterate over all tweet objects for each user..
                # grabs all mentioned users
                mentioned = j['entities']['user_mentions']
                
                # includes mentioned users along with quoted users..
                # we define a target if a tweet is retweeted, or if there is any user mention, or if tweet is quoted from someone else.
                target_all = []
                if mentioned != []:
                    for t in mentioned:
                        if t != None:
                            target_all.append(t['screen_name'])
                            
                    if self.get_quoted_user(j) != None:  #if there is quoted user we also add that to target                 
                        target_all.append(self.get_quoted_user(j))
                
                else:                
                    if self.get_quoted_user(j) != None:                    
                        target_all.append(self.get_quoted_user(j))                
                    
                
                if self.is_retweeted(j): # if tweet is retweeted  
                    
                    if target_all != []:    
                        for k in target_all:
                            fill_df_fields(target_all, k, j)                        

                    else: # if there is no mention in the tweet
                        fill_df_fields(target_all, 'None', j)
                        
                else: # if tweet is not retweeted

                    if target_all != []:    
                        for k in target_all:
                            fill_df_fields(target_all, k, j)
                            
                    else: # if there is no mention in the tweet
                        fill_df_fields(target_all, 'None', j)
                                
        df['Source'] = sources
        df['Target'] = targets
        df['Tweet'] = tweets
        df['Is_quoted'] = is_quoted_all
        df['Is_retweeted'] = is_retweeted_all
        df['Created_at'] = created_at
        df['Favorite_count'] = favorite_count
        df['Media_url'] = media_url_all
        df['Media_url_https'] = media_url_https_all
        df['Media_type'] = media_type_all
        df['Normal_urls'] = normal_url_all
        df['Source_user_id'] = source_user_id
        df['Emojis'] = self.extract_emojis(df)
        df['Image_predictions'] = None
        df = df.reset_index().rename(columns={'index': 'row_id'})
        df = self.img_process.get_image_predictions(df)
        df = self.img_process.getHypernyms(df)
        return df

    def aggregated_dataset(self):
        df = self.create_dataset()
        df_aggregated = df.groupby(['Source', 'Target'], sort=False).size().reset_index(name='Count')
        df_merged = pd.merge(df, df_aggregated, on=['Source','Target'], how='inner')
        df_merged_final = df_merged.groupby(['Source','Target','Count']).agg(lambda x: list(x)).reset_index()
        df_merged_final = df_merged_final.sort_values(by=['Count'], ascending=False).reset_index(drop=True)
        df_merged_final = df_merged_final[df_merged_final['Count'] >= 3]
        df_merged_final = df_merged_final.reset_index().rename(columns={'index': 'Interaction_Id'})
        return df_merged_final
    
