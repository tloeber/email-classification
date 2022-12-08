ludwig-train:
	ludwig train --config ludwig/config.yaml --dataset data/model-input-ludwig-small.jsonl

export-env-linux:
	conda env export > local/conda_env_linux.yml

export-env-windows:
	conda env export > local/conda_env_windows.yml
