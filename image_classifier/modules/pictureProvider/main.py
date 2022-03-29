# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import sys
import os
import requests
import json
import asyncio
from azure.iot.device import IoTHubModuleClient, Message
from azure.iot.device import MethodResponse

# global counters
SENT_IMAGES = 0

# global client
CLIENT = None

# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json
def send_to_hub(strMessage):
    message = Message(bytearray(strMessage, 'utf8'))
    CLIENT.send_message_to_output(message, "output1")
    global SENT_IMAGES
    SENT_IMAGES += 1
    print( "Total images sent: {}".format(SENT_IMAGES) )

# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
            print("Response from classification service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("No response from classification service")
            return None

    return json.dumps(response.json())


async def receive_methodrequest_handler(method):
    if method.name == "classify":
        if("path" in method.payload):
            print("send image")
            classification = sendFrameForProcessing(method.payload.get("path"), IMAGE_PROCESSING_ENDPOINT)
            if classification:
                send_to_hub(classification)
                payload = {"result": True, "data": "execute successfully"}
                method_response = MethodResponse.create_from_method_request(method, 200, payload)
                await CLIENT.send_method_response(method_response)
            else:
                payload = {"data": "Classification failed"}
                method_response = MethodResponse.create_from_method_request(method, 400, payload)
                await CLIENT.send_method_response(method_response)
                
        else:
            payload = {"data": "key is missing"}
            method_response = MethodResponse.create_from_method_request(method, 400, payload)
            await CLIENT.send_method_response(method_response)

            
def main():
    try:
        print ( "Simulated camera module for Azure IoT Edge. Press Ctrl-C to exit." )
        try:
            global CLIENT
            CLIENT = IoTHubModuleClient.create_from_edge_environment()
            CLIENT.on_method_request_received = receive_methodrequest_handler
        except Exception as iothub_error:
            print ( "Unexpected error {} from IoTHub".format(iothub_error) )
            return

        while True:
            print("Application is still running")
            time.sleep(1000)

    except KeyboardInterrupt:
        print ( "IoT Edge module sample stopped" )




if __name__ == '__main__':
    try:
        # Retrieve the image location and image classifying server endpoint from container environment
        IMAGE_PATH = "in direkter Methode definiert"
        IMAGE_PROCESSING_ENDPOINT = "http://classifier/image" #
    except ValueError as error:
        print ( error )
        sys.exit(1)

    if ((IMAGE_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main()
    else: 
        print ( "Error: Image path or image-processing endpoint missing" )