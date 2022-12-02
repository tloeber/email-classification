"""
This is the entry point for the data pipeline, which gets emails from Gmail API,
converting data to tabular format, and saves result as parquet file for
downstream analysis.
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import pickle
from functools import reduce
import logging
import logging.config  # Config needs to be explicitly imported
from typing import Final

import boto3
import yaml

from gmail_client.thread_client import ThreadClient
from data_schemas.gmail.simple_types import ThreadId


PERSIST_RESULTS: Final[bool]  = True
UPLOAD_DATA: Final[bool] = True
FILTER_QUERY: Final[str]  = 'After:2022/10/01'
# Todo: get from same dotenv file that ML uses
BUCKET: Final[str] = 'email-classification-sagemaker'


# Set up logging
with open('conf/logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

s3 = boto3.client('s3')


def main():
    # Validate parameters
    if UPLOAD_DATA and not PERSIST_RESULTS:
        raise Exception(
            "To upload data, you must also set `PERSIT_RESULTS` to true."
        )

    thread_client = ThreadClient()
    df = get_email_data(
        thread_client=thread_client,
        filter_query=FILTER_QUERY,
    )

    if PERSIST_RESULTS:
        # Remove non-ascii characters (e.g., emoticons) which cause trouble with
        # parquet serialization
        df['body'] = df.body.map(
            lambda s: s.encode('ascii', errors='ignore').decode()
        )

        pq.write_table(
            pa.Table.from_pandas(df),
            'data/df.parquet'
        )

    if UPLOAD_DATA:
            s3.upload_file(
            Filename='data/df.parquet',
            Bucket=BUCKET,
            Key='silver/df.parquet'
        )



    if df.index.duplicated().any():
        raise Warning('Found duplicated index values.')


def get_email_data(
    thread_client: ThreadClient,
    filter_query: str
) -> tuple[pd.DataFrame, list[dict]]:
    thread_ids: Final[list[ThreadId]] = thread_client.list_thread_ids(
        query=filter_query
    )

    list_of_dicts = []
    dlq = []  # Todo: start using DLQ class
    for thread_id in thread_ids:
        thread, dlq_i = thread_client._get_thread_with_details(thread_id)
        thread_data = thread.get_transformed_data()
        list_of_dicts.append(thread_data)
        dlq.extend(dlq_i)

    # Combine dictionaries of results into a single dictionary
    dict_of_dicts = reduce(
        lambda dict1, dict2: {**dict1, **dict2},
        list_of_dicts
    )
    data = pd.DataFrame(dict_of_dicts).T

    return data, dlq


if __name__ == '__main__':
    main()
