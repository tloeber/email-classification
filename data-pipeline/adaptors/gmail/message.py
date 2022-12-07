# Enable current type hints for older Python version (<3.10)
from __future__ import annotations
# import pdb; pdb.set_trace()
from data_schemas.gmail.get_thread import RawGmailMessage
from adaptors.interface import MessageAdaptorInterface
from utils.dlq import DLQ


class GmailMessageAdaptorImpl(MessageAdaptorInterface):
    def __init__(self, raw_msg: RawGmailMessage) -> None:
        self.raw_msg = raw_gmail_msg

    dlq: ClassVar[DLQ] = DLQ(name="RawGmailMessage")

    @property
    def sender(self) -> str | None:
        """
        Return sender if found. Otherwise raise Exception.
        """
        for header in self.raw_msg.payload.headers:
            if header['name'] == 'From':
                return header['value']

        # If we end up here, header was not found
        self.dlq.add_message(
            problem="No sender found in message payload.",
            data=self.raw_msg.json()
        )
        return None

    @property
    def body_as_text(self) -> str | None:
        """Get body, decode it, and convert from html to text."""
        # Todo: Consider using polymorphism to simplify logic of getting
        # sender and body for different  MIME types.

        # Check if the default body location contains any data
        payload_has_body: bool = self.raw_msg.payload.body is not None
        payload_body_has_data: bool = self.raw_msg.payload.body.data is not None
        if payload_has_body and payload_body_has_data:
            body: str = self.raw_msg.payload.body.data
            return body

        # Depending on protocol, body may be located elsewhere
        elif self.raw_msg.payload.mime_parts is not None:
            for part in self.raw_msg.payload.mime_parts:
                if part.mime_body and part.mime_body.data is not None:
                    body_encoded: bytes = part.mime_body.data
                    break

            # If we found email body, decode it
            try:
                body_html: bytes = base64.urlsafe_b64decode(body_encoded)
                # ToDo: Explicitly specify bs parser
                return BeautifulSoup(body_html, features='html.parser').get_text()

            # If we didn't find body, `body_encoded` is undefined`. Return None
            except NameError:
                self.dlq.add_message(
                    problem="No body found in message payload.",
                    data=self.raw_msg.json()
                )
                return None

        else:
            raise Exception('It should not bee possible to end up here.')
