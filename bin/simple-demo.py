#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Josh Montague"
__license__="MIT License"

'''
This simple script runs as shown below and assumes there are 
an arbitrary number of .jpg image files in an adjacent directory 
named data. Predictions are sent to standard out (screen). 

$ python simple-demo.py
'''

import glob
from pprint import pprint
import numpy as np
import sys

from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing import image

model = VGG16(weights='imagenet')

# assumes existing image files in data/
for im in glob.glob('data/*.jpg'):
    img = image.load_img(im, target_size=(224,224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    output = decode_predictions(preds, top=5)[0]
    print('filename: {}'.format(im.split('/')[1]))
    print('predictions:')
    pprint(output, stream=sys.stdout)
    print('\n')
