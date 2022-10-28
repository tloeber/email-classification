# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations
from pathlib import Path
import logging
import sys
import json

# Add package root directory to path
package_root_dir = Path(__file__).parent.parent.parent.resolve()
sys.path.append(
    str(package_root_dir)
)
from gmail_client.core_client import CoreClient


PERSIST_RESULTS = True
FILTER_QUERY = 'after:2022/09/01 before:2022/10/01'
THREAD_IDS = ['1838fb7ffac8ba90', '1838e67f60aea615', '1838aa69129f1f74']

logger = logging.getLogger(__name__)


def download_list_threads_response(filter_query, dir: Path):
    """Call gmail API to list threads, and save response for unit testing."""
    response =  thread_client.list(
        userId='me', 
        maxResults=500,
        includeSpamTrash=False, 
        q=filter_query,
    ) \
    .execute()

    filename = test_dir / 'list_threads_result.json'

    with filename.open('w') as file:
        json.dump(obj=response, fp=file)

    print(f"Saved list-threads response to {filename}.")


def download_get_thread_response(thread_id, dir: Path):
    response = thread_client.get(
        userId='me', 
        id=thread_id
    ) \
    .execute()
        
    filename = dir / f'get_thread_{thread_id}.json'

    with filename.open('w') as file:
        json.dump(obj=response, fp=file)

    print(f"Saved list-threads response to {filename}.")


if __name__ == '__main__':
    gmail_client = CoreClient().get_authenticated_client()
    thread_client = gmail_client.users().threads()

    test_dir = Path(__file__).parent.parent.resolve()
    test_data_dir = test_dir / 'data'

    download_list_threads_response(FILTER_QUERY, dir=test_data_dir)
    for thread_id in THREAD_IDS:
        download_get_thread_response(thread_id, dir=test_dir)