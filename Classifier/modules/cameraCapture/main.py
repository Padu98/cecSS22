# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import requests
import json
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse, Message
import asyncio
import base64
import io

def create_client():
    iotclient = IoTHubModuleClient.create_from_edge_environment()
    async def receive_methodrequest_handler(method):
        if method.name == "classify":
            base64_bytes_received = (method.payload).encode('utf-8')
            byte_arr_received = base64.b64decode(base64_bytes_received)
            
            try:
                with open("/images/classify_image.png", "wb") as file:
                    file.write(byte_arr_received)
            except Exception as e:
                print(f"Error while writing file: {e}")
            
            classification = sendFrameForProcessing("/images/classify_image.png", "http://classifier/image")
            print(classification)
            await send_to_hub(classification)
            payload = {"data" : "successfully", "result" : classification}
            method_response = MethodResponse.create_from_method_request(method, 200, payload)
            await iotclient.send_method_response(method_response)
            
        if method.name == "test":
            payload = {"data" : "successfully", "result" : 'test'}
            method_response = MethodResponse.create_from_method_request(method, 201, payload)
            await iotclient.send_method_response(method_response)
        else:
            payload = {"data" : "method not known"}
            method_response = MethodResponse.create_from_method_request(method, 400, payload)
            await iotclient.send_method_response(method_response)

    async def send_to_hub(strMessage):
        message = Message(bytearray(strMessage, 'utf8'))
        await iotclient.send_message_to_output(message, "output1")

 
    def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
        headers = {'Content-Type': 'application/octet-stream'}
        with open(imagePath, mode="rb") as test_image:
            try:
                response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image) #davor dataBytesIO
                print("Response from classification service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
            except Exception as e:
                print(e)
                print("No response from classification service")
                return None

        return json.dumps(response.json())

    print('enter try block!')
    try:
        print('hanler activation')
        iotclient.on_method_request_received = receive_methodrequest_handler
    except:
        print('failed')
        iotclient.shutdown()
        raise
    print('return client')
    return iotclient


async def run_sample(client):
    while True:
        await asyncio.sleep(1000)

def main():
    print('entered main')
    client = create_client()
    print('created client')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print(e)
        raise
    finally:
        loop.run_until_complete(client.shutdown())
        loop.close()



if __name__ == "__main__":
    print('start module')
    main()

