# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import ClassVar

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

logger = logging.getLogger(__name__)


class CoreClient:

    _token_path: ClassVar[Path] = \
        Path(__file__).parent / 'credentials/token.json'
    _credentials_path: ClassVar[Path] = \
        Path(__file__).parent / 'credentials/credentials.json'

    def __init__(self,
        # If modifying these scopes, delete the file token.json.
        scopes: tuple[str] = ('https://www.googleapis.com/auth/gmail.readonly',)
    ):
        # To avoid the danger of mutable default argument, require tuple, then
        # convert to list.
        self.scopes: list[str] = list(scopes)


    def get_authenticated_client(self) -> Resource:
        credentials: Credentials = self.__get_credentials()
        client: Resource = build('gmail', 'v1', credentials=credentials)
        return client

    def __get_credentials(self) -> Credentials:
        """
        Get oAuth credentials.
        """
        def _require_authorization_from_user() -> Credentials:
            flow = InstalledAppFlow.from_client_secrets_file(
                self._credentials_path, self.scopes
            )
            credentials: Credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self._token_path, 'w') as token:
                token.write(credentials.to_json())
            return credentials


        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_found = os.path.exists(self._token_path)
        if token_found:
            credentials = Credentials.from_authorized_user_file(
                self._token_path, self.scopes
            )

            # Refresh expired credentials
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except RefreshError:
                    logger.warning('Refreshing credentials failed.')
                    credentials = _require_authorization_from_user()

            # If there are no credentials available, let the user log in.
            # Note: Do this only *after* trying to refresh credentials!
            if not credentials.valid:
                logger.info('Credentials invalid.')
                credentials = _require_authorization_from_user()

        else:
            logger.info('No token found.')
            credentials = _require_authorization_from_user()

        return credentials
