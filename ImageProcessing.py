import numpy as np
import pandas as pd
import os
from tensorflow import keras
import keras
import tensorflow_hub as hub
from keras.applications import resnet50
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.imagenet_utils import decode_predictions
from tensorflow.keras import layers
import tensorflow.keras.backend as K
import PIL.Image as Image
from ExtractData import Extract
import nltk
from nltk.corpus import wordnet as wn

class ImageProcessing:

    def __init__(self):
        self.extract_obj = Extract()
    
    def get_image_predictions(self, df):
        #Load the ResNet50 model
        resnet_model = resnet50.ResNet50(weights='imagenet')
        #path="/home/hale/Project"

        for filename in os.listdir(self.extract_obj.get_tweet_imgs_path()):
            if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".JPG") or filename.endswith(".JPEG"):       
                #print(filename)
                #target_size = tuple(resnet_model.input.shape.as_list()[1:-1])

                # load an image in PIL format
                original = load_img(self.extract_obj.get_tweet_imgs_path()+'/'+filename, target_size=(224, 224))
                #print('PIL image size',original.size)
                #plt.imshow(original)
                #plt.show()

                # convert the PIL image to a numpy array
                # IN PIL - image is in (width, height, channel)
                # In Numpy - image is in (height, width, channel)
                numpy_image = img_to_array(original)
                #plt.imshow(np.uint8(numpy_image))
                #plt.show()
                #print('numpy array size',numpy_image.shape)

                # Convert the image / images into batch format
                # expand_dims will add an extra dimension to the data at a particular axis
                # We want the input matrix to the network to be of the form (batchsize, height, width, channels)
                # Thus we add the extra dimension to the axis 0.
                image_batch = np.expand_dims(numpy_image, axis=0)
                #print('image batch size', image_batch.shape)
                #plt.imshow(np.uint8(image_batch[0]))

                # prepare the image for the Resnet model
                processed_image = resnet50.preprocess_input(image_batch.copy())

                # get the predicted probabilities for each class
                predictions = resnet_model.predict(processed_image)
                #print(predictions) 
                # convert the probabilities to class labels
                # We will get top 20 predictions

                label = decode_predictions(predictions, top=10)
                index = int(filename.split('.')[2])
                df.at[index, 'Image_predictions'] = label
        return df

    def getHypernyms(self, df):
        synonim = [] # word -- noun -- verb

        for i in df['Image_predictions']: ## i is for only one image. it has 9 predictions
            synDict = {}
            if i is not None:
                for j in range(10): # we iterate over all 10 predictions

                    syns = [] # final list for each word 
                    #print(i[0][j][1]) # returns only the word..
                    #print(len(wn.synsets(i[0][j][1]))) # returns the number of synonims..
                    if len(wn.synsets(i[0][j][1])) > 1: # if the predicted word has more than 1 synonims            
                        #print('Predicted word is {}'.format(i[0][j][1]))
                        #print('Synonims are {}'.format(wn.synsets(i[0][j][1])))
                        nouns = []
                        verbs = []
                        hypers = []
                        for ss in wn.synsets(i[0][j][1]):##for each word in synonims, it finds their corresponding hypernyms.
                            hypers.append(ss.hypernyms())##hypers include all hypernyms for one predicted word..

                        for s in hypers:
                            if s:
                                #print('Hypernym is: {}'.format(s))
                                sParsed = str(s[0])[8:-2] # it was in the form of [Synset('weight.n.02')] we get just the word.
                                newSParsed = sParsed.replace("'", "")
                                newSParsed = newSParsed[:-3]
                                #print(newSParsed)
                                if newSParsed.split('.')[1] == 'n': ## it calculates how many synonims are nouns
                                    nouns.append(newSParsed)
                                elif newSParsed.split('.')[1] == 'v': ## calculates how many synonims are verbs
                                    verbs.append(newSParsed)

                        if len(nouns) >= 2:
                            syns.extend(nouns[0:2])
                        else:
                            syns.extend(nouns)

                        if len(verbs) >= 2:
                            syns.extend(verbs[0:2])
                        else:
                            syns.extend(verbs)

                        synDict[len(synDict)] = {'Word' : i[0][j][1], 'General Form':syns}
                        #print('\n')
                    else:
                        #print('Predicted word is {}'.format(i[0][j][1]))
                        #print('Synonims are {}'.format(wn.synsets(i[0][j][1])))
                        s = wn.synsets(i[0][j][1])[0].hypernyms()
                        sParsed = str(s[0])[8:-2] # it was in the form of [Synset('weight.n.02')] we get just the word.
                        newSParsed = sParsed.replace("'", "")
                        newSParsed = newSParsed[:-3]
                        #print(newSParsed)
                        #print('Hypernym is: {}'.format(newSParsed))
                        syns.append(newSParsed)
                        synDict[len(synDict)] = {'Word' : i[0][j][1], 'General Form':syns}
                        #print('\n')
                    #print('\n')    
                synonim.append(synDict)
            else:
                synonim.append(None)
                
        df['Hypernyms'] = synonim
        return df



