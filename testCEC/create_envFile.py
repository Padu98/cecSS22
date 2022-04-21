import azureml.core
from azureml.core.conda_dependencies import CondaDependencies
import json
from azureml.train.automl.run import AutoMLRun
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
#import azureml.train.automl

m#odel_data = json.load(open('./aml_config/model_config.json'))

#run_id = 'AutoML_905f6984-902e-41ed-9859-536a4a9eff64'
#experiment_name = 'RealTimeInterfacePipelineKlassifizierung'
#model_id = 'TrainSec'

#ws = Workspace.from_config(path='./aml_config')
#experiment = Experiment(ws, experiment_name)

#automl_run = AutoMLRun(experiment = experiment, run_id = run_id)
#best_run, fitted_model = automl_run.get_output()
#iteration = int(best_run.get_properties()['iteration'])
#dependencies = automl_run.get_run_sdk_dependencies(iteration = iteration)


myenv = CondaDependencies.create(conda_packages=['numpy','scikit-learn','pandas','psutil'], pip_packages=['azureml-sdk[automl]'])

conda_env_file_name = 'myenvi.yml'
myenv.save_to_file('.', conda_env_file_name)

# Substitute the actual version number in the environment file.
with open(conda_env_file_name, 'r') as cefr:
    content = cefr.read()

with open(conda_env_file_name, 'w') as cefw:
    cefw.write(content.replace(azureml.core.VERSION, dependencies['azureml-sdk']))