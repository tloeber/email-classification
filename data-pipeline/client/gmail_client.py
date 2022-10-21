# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations 
import os
import logging
from datetime import datetime
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from data_models import Message, NextPageToken, ThreadId, MessageId
from domain_models.email_thread import EmailThread

logger = logging.getLogger(__name__)


class GmailClient:

    def __init__(self, 
        # If modifying these scopes, delete the file token.json.
        scopes: list[str] = ['https://www.googleapis.com/auth/gmail.readonly'],
    ):
        self.scopes = scopes
        
    def get_authenticated_client(self):
        credentials = self.__get_credentials()
        client = build('gmail', 'v1', credentials=credentials)
        return client

    def __get_credentials(self):
        """
        This code is taken from Google-provided boilerplate code with only
        small modifications.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file(
                'token.json', self.scopes
            )
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds
