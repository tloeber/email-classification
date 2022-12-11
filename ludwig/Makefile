ludwig-train:
	ludwig train --config config.yaml --dataset ../data/model-input-ludwig-small.jsonl

ludwig-train-on-fake-data:
	ludwig train --config config.yaml --dataset bug_reports/data/fake-data.jsonl

delete-ludwig-temp-datesets:
	ls data/*.parquet | xargs rm
	ls data/*.hdf5 | xargs rm
	ls bug_reports/data/*.parquet | xargs rm
	ls bug_reports/data/*.hdf5 | xargs rm
