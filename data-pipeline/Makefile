create-env:
	pip install pipenv && pipenv install

# Note: Usually, you don't want to do this manually. Instead, set the IDE to use
# the right virtual environment.
activate-env:
	pipenv shell

run-static-analysis:
	mypy .

run-data-pipeline:
	python main .py

visualize-code-flow:
	code2flow main.py
