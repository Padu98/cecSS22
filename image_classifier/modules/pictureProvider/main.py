# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import os
import requests
from azure.iot.device import IoTHubModuleClient, Message

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import ast
import glob, os
import asyncio
from http import client
from pkgutil import ImpImporter
import sys
import signal
import threading
from unittest import case, result
from urllib import response
from azure.iot.device.aio import IoTHubModuleClient
import json
from azure.iot.device import MethodResponse


cert = 'certs/client_certificate.pem'
private_key = 'certs/private_key_client.pem'


# Event indicating client stop
stop_event = threading.Event()


def create_client():
    iotclient = IoTHubModuleClient.create_from_edge_environment()
    ##function for receiving method requests

    async def receive_methodrequest_handler(method):
        if method.name == "classify":
            if("path" in method.payload):
                classification = sendFrameForProcessing(method.payload.get("path"), "http://classifier/image")
                #print(classification)
                if classification:
                   # print("send classification result to iot hub")
                    print("result: " + classification)
                    await send_to_hub(classification)
                    payload = {"data": "execute successfully"}
                    method_response = MethodResponse.create_from_method_request(method, 200, payload)
                    await iotclient.send_method_response(method_response)
                else:
                    print("classification not succesfully")
                    payload = {"data": "Classification failed"}
                    method_response = MethodResponse.create_from_method_request(method, 400, payload)
                    await iotclient.send_method_response(method_response)
            else:
                payload = {"data": "key is missing"}
                method_response = MethodResponse.create_from_method_request(method, 400, payload)
                await iotclient.send_method_response(method_response)
        elif method.name == "sortAll":
            discocytes = []
            echitocytes = []
            spherocytes = []
            prob = []

            os.chdir("/Images")
            for file in glob.glob("*.jpg"):
                classification = sendFrameForProcessing("/Images/" + file, "http://classifier/image")
                classification_json = json.loads(classification)
                predictions = classification_json["predictions"]
                for index in range(len(predictions)):
                    prediction = predictions[index]
                    if prediction["probability"] < 0.9:
                        prob.append(file + " is " + prediction["tagName"])
                    elif prediction["tagName"] == "discocytes":
                        discocytes.append(file)
                    elif prediction["tagName"] == "echinocytes":
                        echitocytes.append(file)
                    elif prediction["tagName"] == "spherocytes":
                        spherocytes.append(file)
                    

            resultDict = {"discocytes" : discocytes, "echitocytes": echitocytes, "spherocytes": spherocytes, "probability less 90%" : prob}
            print(resultDict)
            print("\n")
            await send_to_hub(json.dumps(resultDict))
            payload = {"result": True, "data": "success"}
            method_response = MethodResponse.create_from_method_request(method, 200, payload)
            await iotclient.send_method_response(method_response)
        else:        
            print("method could not be identified")
            payload = {"result": True, "data": "execute fail"}
            method_response = MethodResponse.create_from_method_request(method, 400, payload)
            await iotclient.send_method_response(method_response)

    
    # Send an image to the image classifying server
    # Return the JSON response from the server with the prediction result
    def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
        headers = {'Content-Type': 'application/octet-stream'}
       # print(imagePath)

        with open(imagePath, mode="rb") as test_image:
            try:
                response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
        #        print("Response from classification service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
            except Exception as e:
                print(e)
                print("No response from classification service")
                return None
        return json.dumps(response.json())


    async def send_to_hub(strMessage):
        message = Message(bytearray(strMessage, 'utf8'))
        await iotclient.send_message_to_output(message, "output1")
       # global SENT_IMAGES
        #SENT_IMAGES += 1
        #print( "Total images sent: {}".format(SENT_IMAGES) )

    try:
        iotclient.on_method_request_received = receive_methodrequest_handler
    except:
        iotclient.shutdown()
        raise

    return iotclient


async def run_sample(client):
    while True:
        await asyncio.sleep(1000)


def main():
    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
