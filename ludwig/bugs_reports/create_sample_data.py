import numpy as np
import pandas as pd
# import  numpy.typing as npt
from essential_generators import DocumentGenerator


N_ROWS: int = 30
SEED: int = 1

random_nr_generator: np.random.Generator = np.random.default_rng(seed=SEED)
replied_to = random_nr_generator.choice(
    [False, True],
    size = N_ROWS,
    p=[0.9, 0.1]  # 90% will be `False`
)
split = random_nr_generator.choice(
    [0, 1, 3],
    size = N_ROWS,
    p=[0.4, 0.3, 0.3]  # Split 40/30/30
)


document_generator = DocumentGenerator()
sender: list[str] = [
    document_generator.email() for _ in range(N_ROWS)
]

body: list[str] = [
    document_generator.paragraph() for _ in range(N_ROWS)
]

df = pd.DataFrame({
    'replied_to': replied_to,
    'sender':sender,
    'body': body,
    'split': split,

})

print(df)
