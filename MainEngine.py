import pandas as pd
from ExtractData import Extract
from Transformation import Transformation
from ExtractImages import ExtractImages
from test_calc import TestConfig
from RegexConfig import Configuration
class MainEngine:
    ext_img = ExtractImages()
    trans_obj = Transformation()
if __name__ == '__main__':
    main_obj = MainEngine()
    
    # Uncomment to download the profile images.. It should run only once..
    # main_obj.ext_img.download_profile_images()

    # Uncomment to download the images attached to tweets.. This should run only once.
    # main_obj.ext_img.download_tweet_images()
    
    
    # this gives the final dataset..
    # final dataset is loaded into excel..
    final_dataset = main_obj.trans_obj.aggregated_dataset()
    final_dataset.to_excel("~/final_dataset.xlsx")
