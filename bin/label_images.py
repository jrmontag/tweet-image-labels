#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Josh Montague"
__license__="MIT License"

import argparse
from io import BytesIO
import logging
import sys

import numpy as np
from PIL import Image
from pprint import pprint
import requests
try:
    import ujson as json
    JSON_error = ValueError
except ImportError as e:
    import json
    JSON_error = json.JSONDecodeError
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.utils.data_utils import get_file




def get_model(model_name):
    """
    Create and return a Keras model with pre-trained weights.
     
    Parameters
    ----------
    model_name : str 
        Name of model. Supported values are: 'vgg16' 

    Returns
    -------
    model
        Keras Model with pre-trained VGG16 weights.  
    """
    supported_models = ['vgg16']

    if model_name not in supported_models:
        raise NotImplementedError('Supported models are: {}'.format(supported_models)) 
    else:
        logging.info('instantiating {} model with pre-trained weights'.format(model_name))
        model = VGG16(weights='imagenet')
    return model

def get_image_from_tweet(tweet):
    """
    Extract an image file from the URL in a given Tweet.  
     
    Parameters
    ----------
    tweet : dict 
        Tweet in JSON-formatted dict structure 

    Returns
    -------
    image 
        PIL-formatted image file (or None) 
    """
    image = None
    # navigate to image field (format-dependent) 
    img_url = _get_img_url(tweet) 
    # use requests to get the binary file
    # TODO: try/except around http errors
    if img_url: 
        image = _download_image(img_url) 
    else:
        logging.info('failed to get image for tweet id={}'.format(tweet['id']))
    # TODO: consider using local cache for image file
    return image

def _get_img_url(tweet):
    """
    Helper function to extract an image URL (or None) from a Tweet.
    Currently supports only Activity Streams format. Handles (potential non-) 
        existance of relevant payload elements.
     
    Parameters
    ----------
    tweet : dict 
        Tweet in JSON-formatted dict structure 

    Returns
    -------
    url : str
        String URL to image location (on twitter.com server) (or None) 
    """
    media_url = None

    # TODO: add support for Original Format Tweets 
    if 'twitter_entities' not in tweet or 'media' not in tweet['twitter_entities']:
        logging.info('no image found in tweet id={}'.format(tweet['id']))
        return media_url 
    try:
        # TODO: account for multiple images in the tweet, and different media types (?) 
        media_url = tweet['twitter_entities']['media'][0]['media_url'] 
    except KeyError:
        logging.info('Failed to extract image URL for tweet id={}'.format(tweet['id']))
    return media_url
 
def _download_image(img_url):
    """
    Download the image located at the given URL.

    This method overlaps with keras.preprocessing.image.load_img(), but 
    does not look to a local file path. See also: 
    https://github.com/fchollet/keras/blob/master/keras/preprocessing/image.py 
     
    Parameters
    ----------
    img_url : str 
        String URL to location of image. 

    Returns
    -------
    image 
        PIL-formatted image file (or None) 
    """
    image = None
    # download binary (requests)
    response = requests.get(img_url)
    # read binary data into PIL.Image
    if response.ok:
        image = Image.open(BytesIO(response.content))
    else:
        logging.info('HTTP error={} for URL={}'.format(response.status_code, img_url)) 
    return image 


def make_predictions(model, img_binary, topk=5):
    """
    Use `model` to generate image label predictions on 
    `img_binary` image. 

    This method follows the examples from the Keras image classification
    documentation. See also: 
    https://keras.io/applications/#usage-examples-for-image-classification-models

    This method overlaps with keras.preprocessing.image.load_img(), but 
    decouples the file read from the image resizing. See also: 
    https://github.com/fchollet/keras/blob/master/keras/preprocessing/image.py 

    Parameters
    ----------
    model : Instance of model from keras.applications 
        Currently only supports VGG16 

    img_binary : PIL-formatted image binary file-like object 

    topk: int
        Top-`k` predictions which will be included in results 
        
    Returns
    -------
    output : list 
        Named model predictions and confidence scores 
    """
    # TODO: define a useful results object
    # TODO: choose (top-)k as CLI arg
    
    # ensure 3-channel image 
    img = img_binary.convert('RGB')

    # resize image according to model specs 
    # TODO: better understand if resizing is necessary/helpful 
    # TODO: introspect model (and  for model => target_size mapping
    target_size = (224,224)

    img = img.resize((target_size[1], target_size[0]))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    # models return a numpy array of predictions
    preds = model.predict(x)
    # translate to top-k named labels
    output = decode_predictions(preds, top=5)[0]
    return output 


def output_results(tweet, results):
    """
    Send `results` predictions for `tweet` to appropriate output location.
    Current output is sys.stdout 


    Parameters
    ----------
    tweet : dict 
        Tweet in dict structure 

    results : list 
        List of top (code, description, probability) prediction tuples 

    Returns
    -------
    None 
    """
    results_array = []

    tweet_id = tweet['id'].split(':')[-1]
    img_url = _get_img_url(tweet) 

    # this is an easy-to-read stdout format
#    sys.stdout.write('tweet id={}\n'.format(tweet_id)) 
#    sys.stdout.write('image url={}\n'.format(img_url)) 
#    sys.stdout.write('predictions={}\n'.format(results)) 
#    sys.stdout.write('\n'*2)

    # this is the TSV stdout format for downstream analysis
    results_array.append(tweet_id)
    results_array.append(img_url)

    for item in results:
        results_array.append( item[1] )
        results_array.append( item[2] )

    sys.stdout.write(','.join([str(x) for x in results_array]))
    sys.stdout.write('\n')

    return None 


if __name__ == '__main__':

    # CLI args
    parser = argparse.ArgumentParser(description='Process Tweets from stdin and label attached images')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='increase logging verbosity')
    parser.add_argument('-m', '--model', default='vgg16', 
                        help='select model architecture (default: %(default)s)')
    parser.add_argument('-k', '--topk', type=int, default=5, 
                        help='return top-k predictions for each image (default: %(default)s)') 
    parser.add_argument('-l', '--logpreds', action='store_true', 
                        help='send predictions to logfile') 
    args = parser.parse_args()

    # logging
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                        stream=sys.stderr, level=loglevel)
    logging.debug('logging enabled - preparing for work') 

    # instantiate Keras model 
    model = get_model(args.model)
  
    # read input stream 
    # TODO: add more flexible input (file reads) 
    cntr = 0 
    for line in sys.stdin: 
        try:
            tweet = json.loads(line) 
        except JSON_error as e: 
            logging.info('Failed to parse record. Skipping.')
            logging.debug('Bad record={}'.format(line))
            continue
        cntr += 1
        if cntr % 100 == 0:
            logging.info('observed a total of {} tweets'.format(cntr))
            logging.debug('analyzing tweet id {}'.format(tweet['id']))
            
        # (possibly) get image from tweet 
        img = get_image_from_tweet(tweet)
        if img:
            # make predictions, get results obj 
            pred_results = make_predictions(model, img, args.topk)  

            # write results to correct output stream 
            if args.logpreds:
                tweet_id = tweet['id'].split(':')[-1]
                logging.info('predictions for tweet id {} = {}'.format(tweet_id, pred_results))
                 
            output_results(tweet, pred_results) 
        else:
            # no image retreived for this tweet
            continue

