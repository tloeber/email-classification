"""
This package defines the schemas for the data that we expect to receive from
the Gmail API. These schemas are used by Pydantic to parse the data, and to
raise an exception if the data cannot be coereced into the respective schema.

This specific module defines all schemas for *listing* threads.

Note that these classes are data structures, not `real` classes: They expose
their data rather than behavior. (The behavior is defined in the `email_domain`
package, and is decoupled from the data schemas that particular email APIs use.)
"""

# Enable current type hints for older Python version (<3.10)
from __future__ import annotations

from pydantic import BaseModel

from data_schemas.gmail.simple_types import NextPageToken, ThreadId


# Customize Pydantic base model
# =============================

class CustomBaseModel(BaseModel):
    """
    Configured the validation behavior to *allow but ignore* extra fields
    passed to constructor
    """
    class Config:
        extra = 'ignore'


# Top-level data structure
# ========================

class RawThreadsList(CustomBaseModel):
    """Response callling `list` on the threads API."""
    nextPageToken: NextPageToken
    threads: list[RawThreadSummary]


# *Inner* data structures
# -----------------------

class RawThreadSummary(CustomBaseModel):
    """
    This class models an individual thread in the `list threads` response. Note
    that - by contrast to a `get thread` call, it does not contain all the
    details of a thread.
    """
    id: ThreadId
    # History id is a unique identifier about when a thread was last updated.
    # Persist for data versioning.
    historyId: str