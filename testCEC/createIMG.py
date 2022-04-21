from azureml.core.image import Image, ContainerImage
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
from azureml.core.model import Model
from azureml.core import Environment

import pickle
import json
import numpy as np
import pandas as pd
from azureml.core.model import Model


AZURE_SUBSCRIPTION_ID = 'ba16188a-6c52-460f-b7b3-3410052ed582'
ML_WORKSPACE_NAME = 'mlWorkspaceSS22'
AZURE_IOT_HUB_NAME = 'cecSS22-iothub'
RESOURCE_GROUP_NAME = 'cec-projekt1-ML'
LOCATION = 'Germany West Central'
STORAGE_ACCOUNT_NAME = 'mlworkspacess21834533704'
STORAGE_ACCOUNT_KEY = 'N1nG26QK1Ra8rQf3Rl2dgSCVj15PRSOxFPaBNcce5nESWGP0KqzqJdH01HUce3J+9ZR/WCKnvSAeSN1HNL9OKA=='
STORAGE_ACCOUNT_CONTAINER = 'blutkoerperchen'

import os, glob, shutil

if not os.path.exists('./data'):
    os.mkdir('./data')

for f in glob.glob('./*.txt') + glob.glob('./*.csv'):
    shutil.move(f, './data/')

from azureml.core import Workspace
workspace_name = ML_WORKSPACE_NAME
subscription_id = AZURE_SUBSCRIPTION_ID
resource_group = RESOURCE_GROUP_NAME
location = LOCATION

if not os.path.exists('./aml_config'):
    os.mkdir('./aml_config')

#check to see if the workspace has already been created and persisted
if (os.path.exists('./aml_config/.azureml/config.json')):
    ws = Workspace.from_config(path='./aml_config')
else:
    ws = Workspace.create(name=workspace_name,
                          subscription_id=subscription_id,
                          resource_group=resource_group,
                          create_resource_group=True,
                          location=location
                         )

    ws.write_config(path='./aml_config')

if (AZURE_SUBSCRIPTION_ID == ''
        or ML_WORKSPACE_NAME == ''
        or AZURE_IOT_HUB_NAME == ''
        or RESOURCE_GROUP_NAME == ''
        or LOCATION == ''
        or STORAGE_ACCOUNT_NAME == ''
        or STORAGE_ACCOUNT_KEY == ''
        or STORAGE_ACCOUNT_CONTAINER == ''):
    raise ValueError('All values must be filled in') 

ws = Workspace.from_config(path='./aml_config')
model = Model(ws, 'TrainSec')

image_config = ContainerImage.image_configuration(runtime= "python",
                                 execution_script = 'score.py',
                                 conda_file = 'conda_env.yaml',
                                 tags = {'area': "digits", 'type': "automl_classification"},
                                 base_image = 'arm32v7/python:3.9-alpine',
                                 description = "Image for Edge ML samples",
                                 docker_file="Dockerfile.arm32v7")



image = Image.create(name = "classifierimage",
                     # this is the model object 
                     models = [model],
                     image_config = image_config, 
                     workspace = ws)

image.wait_for_creation(show_output = True)

if image.creation_state == 'Failed':
    print("Image build log at: " + image.image_build_log_uri)