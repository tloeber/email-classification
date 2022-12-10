import datetime
from typing import NoReturn, Literal
from pathlib import Path
# import logging

import numpy as np
import pandas as pd
# import  numpy.typing as npt
from essential_generators import DocumentGenerator
from faker import Faker

N_ROWS: int = 30
SEED: int = 1  # Both for numpy and faker
START_DATE: datetime.date = datetime.date(year=2020, month=1, day=1)
RELATIVE_END_DATE: str = '+2y'
RELATIVE_OUTPUT_PATH: str = 'bug_reports/data/fake-data.jsonl'

# logger = logging.getLogger(__name__)


def create_full_dataset(
    n_rows: list[int],
    start_date: datetime.date,
    relative_end_date: str,
    data_output_path: Path | str,
) -> None | NoReturn:
    """
    Create fake test data. The training, validation, and test sets will be
    created separately by a helper function. This makes a number of things
    easier:
    - Making sure that all categories of the label (or other important
    categorical variable) are present in every category.
    - Model dependent data (in particular, time-series).

    So far, only stratification by label is implemented. An exception will be
    raised if both categories are not present in every split.
    """
    # Input validation
    assert len(n_rows) == 3

    df_train: pd.DataFrame = _create_partial_dataset(
        n_rows=n_rows[0],
        start_date=start_date,
        relative_end_date=relative_end_date,
        split=0
    )

    df_test: pd.DataFrame = _create_partial_dataset(
        n_rows=n_rows[1],
        start_date=start_date,
        relative_end_date=relative_end_date,
        split=1
    )

    df_val: pd.DataFrame = _create_partial_dataset(
        n_rows=n_rows[2],
        start_date=start_date,
        relative_end_date=relative_end_date,
        split=2
    )

    df_all: pd.DataFrame = pd.concat(
        [df_train, df_test, df_val],
        axis='rows',
    )

    print(df_all.head())

    # Write JSONLines
    with open(data_output_path, 'w') as f:
        f.write(
            df_all.to_json(orient='records', lines=True)
        )
    print(f'Wrote data to {data_output_path}')


def _create_partial_dataset(
    n_rows: int,
    start_date: datetime.date,
    relative_end_date: str,
    split: Literal[0, 1, 2],
) -> pd.DataFrame:
    """
    This helper function create data for EITHER train, test, OR validation set.
    The `split` argument determines which of these will be created.
    """

    replied_to = random_nr_generator.choice(
        [False, True],
        size = n_rows,
        # Todo: create test, val, and train data separately
        p=[0.2, 0.8],  # Relatively balanced.
    )
    unique_labels = set(replied_to)
    if len(unique_labels) != 2:
        raise Exception(
            'Not all classes present in randomly generated labels. Please '
            'increase sample size or make class probabilities more balanced.'
        )

    document_generator = DocumentGenerator()
    sender: list[str] = [
        document_generator.email() for _ in range(n_rows)
    ]

    body: list[str] = [
        document_generator.paragraph() for _ in range(n_rows)
    ]


    time_received: list[str] = [
        _generate_random_datetime_string(
            start_date=start_date,
            relative_end_date=relative_end_date,
        )
        for _ in range(n_rows)
    ]


    df = pd.DataFrame({
        'replied_to': replied_to,
        'sender':sender,
        'body': body,
        'split': split,
        'time_received': time_received,
    })
    return df


def _generate_random_datetime_string(
    start_date: datetime.date | datetime.datetime,
    relative_end_date: str,
) -> str:
    """
    Generate random daytime and convert to string.

    This is necessary when data frame is converted to JSON lines, because
    otherwise the time will be converted to integer (UNIX timestamp).
    """
    random_datetime = fake_data_generator.date_time_between(
            start_date=start_date,
            end_date=relative_end_date,
        )
    return f'{random_datetime:%Y-%m-%d %H:%M:%S}'


if __name__ == '__main__':
    random_nr_generator: np.random.Generator = np.random.default_rng(seed=SEED)
    fake_data_generator = Faker()
    Faker.seed(SEED)

    # Even though utils/absolute_paths.py doors this variable, we cannot access
    # this module easily from here. The simplest solution is to simply re-create
    # it, rather than messing with relative imports or modifying sys.path.
    LUDWIG_ROOT_DIR: Path = (
        Path(__file__)
            .parent  # bug_reports/
            .parent  # ludwig/
            .resolve()
    )
    absolute_data_output_path: Path = LUDWIG_ROOT_DIR / RELATIVE_OUTPUT_PATH

    create_full_dataset(
        n_rows=[10, 10, 10],
        start_date=START_DATE,
        relative_end_date=RELATIVE_END_DATE,
        data_output_path=absolute_data_output_path,
    )
