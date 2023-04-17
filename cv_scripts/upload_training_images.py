#!/usr/bin/env python3

import requests
import os
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry
from azure.identity import DefaultAzureCredential
from msrest.authentication import ApiKeyCredentials


ENDPOINT = 'https://ceccvampadu.cognitiveservices.azure.com/'
PROJECT_ID = '87d15d8f-c21e-447b-8a91-46db70147cd0'

TAG_ID_ECHINOZYT = '2dc925b0-7432-41bc-97a5-2105f48cd105'
TAG_ID_SPHAEROZYT = '5a4b343e-9b42-445f-9928-3953e39b8e8f'
TAG_ID_DISKOZYT = 'ddcd2d20-8db2-407b-840b-9dc369b30a4a'

IMAGE_PATH_ECHINOZYT =  './Portraits_png/Echinocytes-Test/'
IMAGE_PATH_SPHAEROZYT = './Portraits_png/Spherocytes-Test/'
IMAGE_PATH_DISKOZYT = './Portraits_png/Discocytes-Test/'

############### bad practice!!!
TRAINING_KEY = 'ad94676cbf9f475585d8dea3ac58b1fa'
os.environ['AZURE_COGNITIVE_SERVICES_KEY'] = TRAINING_KEY
#credential = DefaultAzureCredential()
credential = ApiKeyCredentials(in_headers={"Training-key": TRAINING_KEY})
############### bad practice!!!


path_array = [IMAGE_PATH_ECHINOZYT, IMAGE_PATH_SPHAEROZYT, IMAGE_PATH_DISKOZYT]
id_array = [TAG_ID_ECHINOZYT, TAG_ID_SPHAEROZYT, TAG_ID_DISKOZYT]
for i in range(len(path_array)):
    IMAGE_DIR = path_array[i]
    TAG_ID = id_array[i]

    trainer = CustomVisionTrainingClient(endpoint=ENDPOINT, credentials = credential)

    image_list = []

    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith(".png") or filename.endswith(".png'"):
            with open(os.path.join(IMAGE_DIR, filename), "rb") as image_contents:
                image_list.append(ImageFileCreateEntry(name=filename, contents=image_contents.read(), tag_ids=[TAG_ID]))

        if len(image_list) > 63:
            upload_result = trainer.create_images_from_files(PROJECT_ID, ImageFileCreateBatch(images=image_list))
            image_list.clear()
            print('uploaded 64 images.')


    #upload the rest
    upload_result = trainer.create_images_from_files(PROJECT_ID, ImageFileCreateBatch(images=image_list))
    print(IMAGE_DIR + ' done!')
    
print('go to cv page to see if upload was successfully.')