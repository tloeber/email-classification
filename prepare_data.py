# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from functools import reduce
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa


from thread_api import list_all_thread_ids, _get_thread_with_details

PERSIST_RESULTS = True
FILTER_QUERY = 'After:2018/01/01'

class Counter:
    # ToDo: Add logging every, say, 100 API calls
    def __init__(self):
        self.state = 0

    def increment(self):
        self.state += 1


def _strip_non_ascii_chars(string_: str) -> str:
    return string_.encode('ascii', errors='ignore').decode()


def main():
    thread_ids = list_all_thread_ids(
        query=FILTER_QUERY
    )

    list_of_dicts = []
    for thread_id in thread_ids:
        thread, dlq = _get_thread_with_details(thread_id)
        thread_data = thread.get_transformed_data()
        list_of_dicts.append(thread_data)
        
    dict_of_dicts = reduce(
        lambda dict1, dict2: {**dict1, **dict2},
        list_of_dicts
    )

    df = pd.DataFrame(dict_of_dicts) \
    .T

    # Put data in the right format for ML
    # ToDo: Move this to EDA notebook and preserve original data
    df = df.assign(
        target = df.replied_to.astype('int'),
        input = (df.sender + ' ' + df.body) \
            .map(_strip_non_ascii_chars) 
    )
    if PERSIST_RESULTS:
        pq.write_table(
            pa.Table.from_pandas(df[['target', 'input']]), 
            'df.parquet'
        )

    print(
        df.head(10),
        df.shape,
        df.replied_to.sum()
    )

    if df.index.duplicated().any():
        raise Warning('Found duplicated index values.')
    
if __name__ == '__main__':
    main()