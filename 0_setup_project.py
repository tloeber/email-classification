from smexperiments.experiment import Experiment

EXPERIMENT_NAME = 'emailClassification-blazingText'


# Create Sagemaker Experiment
# ===========================

# This which will track individual trials
experiment = Experiment.create(
	experiment_name=EXPERIMENT_NAME,
	description='Predict which emails will elicit response.',
	tags=[
		{'Key': 'project', 'Value': 'email-classification'},
		{'Key': 'algorithm', 'Value': 'blazing-text'}
	]
)
