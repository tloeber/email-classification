from datetime import datetime
import logging


class DLQ:
    """
    Dead letter queue to store messages that failed to process correctly.
    """
    def __init__(self, logger: logging.Logger, name: str = None) -> None:
        self.logger = logger
        self.records = []
        self.name = name

    def add_message(
        self, 
        problem: str, 
        exception: Exception | None = None,
        message: dict
    ):
        logger.warning(f'{problem}. {exception}')
        dlq.append(
            {
                "problem": problem,
                "exception": msg,
                "message": dict,
                "timestamp": f'{datetime.now}'
            }
        )
