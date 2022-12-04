ludwig:
	ludwig train --config ludwig/config.yaml --dataset data/model-input-ludwig-small.jsonl

delete-ludwig-temp-datesets:
	ls data/*.parquet | xargs rm
	ls data/*.hdf5 | xargs rm

export-env-linux:
	conda env export > local/conda_env_linux.yml

export-env-windows:
	conda env export > local/conda_env_windows.yml
