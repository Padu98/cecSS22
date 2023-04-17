#!/usr/bin/env python3

import requests

ENDPOINT = "https://ceccvampadu.cognitiveservices.azure.com/customvision/v3.3/training/projects/87d15d8f-c21e-447b-8a91-46db70147cd0/tags"
TRAINING_KEY = "ad94676cbf9f475585d8dea3ac58b1fa"

response = requests.get(ENDPOINT, headers={"Training-Key": TRAINING_KEY})
tags = response.json()


for tag in tags:
    print(tag["name"], tag["id"])
