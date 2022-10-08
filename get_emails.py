from __future__ import print_function

import os.path
from typing import Callable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']



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

    creds = _authenticate()
    
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    # TODO: Handle errors from gmail API If using this function in non-interactive way!
    labels = results.get('labels', [])
    
    if not labels:
        print('No labels found.')
        return
    
    print('Labels and their IDs:')
    for label in labels:
        print(f"{label['name']} : {label['id']}")
    return labels


def show_chatty_threads():
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds, _ = google.auth.default()

    try:
        # create gmail api client
        service = build('gmail', 'v1', credentials=creds)

        # pylint: disable=maybe-no-member
        # pylint: disable:R1710
        threads = service.users().threads().list(userId='me').execute().get('threads', [])
        for thread in threads:
            tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
            nmsgs = len(tdata['messages'])

            # skip if <3 msgs in thread
            if nmsgs > 2:
                msg = tdata['messages'][0]['payload']
                subject = ''
                for header in msg['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                if subject:  # skip if no Subject line
                    print(F'- {subject}, {nmsgs}')
        return threads

    except HttpError as error:
        print(F'An error occurred: {error}')


if __name__ == '__main__':
    show_chatty_threads()

def main():
    list_labels()

if __name__ == '__main__':
    main()