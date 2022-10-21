import pdb
import pickle 
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import pdb

with open('df.pickle', 'rb') as f:
    df: pd.DataFrame = pickle.load(f)

print(df.head())
print(df.shape)

pdb.set_trace()
