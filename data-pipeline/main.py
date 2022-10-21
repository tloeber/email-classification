"""
This is the entry point for the data pipeline, which gets emails from Gmail API,
converting data to tabular format, and saves result as parquet file for 
downstream alysis.
"""

# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import pickle
from functools import reduce
import logging

from client.thread_client import ThreadClient


PERSIST_RESULTS = True
FILTER_QUERY = 'After:2022/10/01'

logger = logging.getLogger(__name__)


def main():
    thread_client = ThreadClient()
    df = get_email_data(
        thread_client=thread_client,
        filter_query=FILTER_QUERY,
    )

    if PERSIST_RESULTS:
        # Temp: Pickle first, so we don't loose data if writing pq dfails
        with open('df.pickle', 'wb') as f:
            pickle.dump(obj=df, file=f)

        # Remove non-ascii characters (e.g., emoticons) which cause trouble with
        # parquet serialization
        df['body'] = df.body.map(
            lambda s: s.encode('ascii', errors='ignore').decode()
        )

        pq.write_table(
            pa.Table.from_pandas(df), 
            'df.parquet'
        )

    print(
        df.head(10),
        df.shape,
        df.replied_to.sum()
    )

    if df.index.duplicated().any():
        raise Warning('Found duplicated index values.')
    
def get_email_data(thread_client, filter_query):
    thread_ids = thread_client.list_all_thread_ids(
        query=filter_query
    )

    list_of_dicts = []
    dlq = []
    for thread_id in thread_ids:
        thread, dlq_i = thread_client._get_thread_with_details(thread_id)
        thread_data = thread.get_transformed_data()
        list_of_dicts.append(thread_data)
        dlq.extend(dlq_i)

    dict_of_dicts = reduce(
        lambda dict1, dict2: {**dict1, **dict2},
        list_of_dicts
    )
    data = pd.DataFrame(dict_of_dicts).T
    
    return data, dlq


if __name__ == '__main__':
    main()
