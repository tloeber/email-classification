# Enable current type hints for older Python version (<3.10)
from __future__ import annotations
from pathlib import Path
import logging
import logging.config  # Config needs to be explicitly imported
import sys
import json
import yaml

# Add package root directory to path.
# todo: Find better solution.
package_root_dir = Path(__file__).parent.parent.parent.resolve()
sys.path.append(
    str(package_root_dir)
)
from gmail_client.thread_client import ThreadClient


PERSIST_RESULTS = True
FILTER_QUERY = 'after:2022/09/01 before:2022/10/01'
THREAD_IDS = ['1838fb7ffac8ba90', '1838e67f60aea615', '1838aa69129f1f74']

logging_config_path: str = f'{package_root_dir}/conf/logging.yaml'
with open(logging_config_path, 'r') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


class TestDataDownloader:

    def __init__(self, download_dir: Path) -> None:
        self.thread_client = ThreadClient()
        self.download_dir = download_dir

    def download_list_threads_response(self, filter_query):
        """
        Call gmail API to *list* threads, and save response for unit testing.
        """
        # pylint: disable=protected-access
        response =  self.thread_client._list_thread_ids_raw(
            query=filter_query,
            next_page_token=None
        )

        file_path = self.download_dir / 'list_threads_result.json'
        with open(file_path, 'w') as file:
            json.dump(obj=response, fp=file)
        print(f"Saved list-threads response to {self.download_dir}.")

    def download_get_thread_response(self, thread_id):
        response = self.thread_client.get_thread(thread_id=thread_id)

        file_path = self.download_dir / f'get_thread_{thread_id}.json'
        with open(file_path, 'w') as file:
            json.dump(obj=response, fp=file)

        print(f"Saved list-threads response to {file_path}.")


if __name__ == '__main__':
    test_dir = Path(__file__).parent.parent.resolve()
    test_data_dir = test_dir / 'data'

    downloader = TestDataDownloader(
        download_dir=test_data_dir,
        )

    # downloader.download_list_threads_response(FILTER_QUERY, dir=test_data_dir)
    for thread_id in THREAD_IDS:
        downloader.download_get_thread_response(thread_id)
