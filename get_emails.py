from __future__ import print_function

import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def create_gmail_client():
    creds = _authenticate()

    # create gmail api client
    client = build('gmail', 'v1', credentials=creds)
    return client


def _authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def list_labels():
    gmail_client = create_gmail_client()
    results = gmail_client.users().labels() \
        .list(userId='me') \
        .execute()

    # TODO: Handle errors from gmail API If using this function in non-interactive way!
    labels = results.get('labels', [])
    
    if not labels:
        print('No labels found.')
        return
    
    print('Labels and their IDs:')
    for label in labels:
        print(f"{label['name']} : {label['id']}")
    return labels


def _list_threads_by_page(next_page_token=None):
    gmail_client = create_gmail_client()

    response = gmail_client.users().threads() \
        .list(userId='me', maxResults=500, pageToken=next_page_token) \
        .execute()
        
    threads = response.get('threads', [])
    next_page_token = response.get('nextPageToken')

    return threads, next_page_token


def list_all_threads() -> List:
    all_threads = []
    next_page_token = None
    while True:
        threads, next_page_token = _list_threads_by_page(next_page_token)
        all_threads.extend(threads)

        # Exit loop once no more pages are left
        if not next_page_token:
            return all_threads


def main():
    # list_labels()
    threads = list_all_threads()
    # for thread in threads:
    #     print(thread)
    print(len(threads))

if __name__ == '__main__':
    main()