# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from functools import reduce
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import pickle

from thread_api import list_all_thread_ids, _get_thread_with_details

PERSIST_RESULTS = True
FILTER_QUERY = 'After:2017/01/01'


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
    
if __name__ == '__main__':
    main()
