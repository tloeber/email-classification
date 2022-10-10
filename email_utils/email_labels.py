# Enable current type hints for older Python version (<3.10) 
from __future__ import annotations 

import email_utils.gmail_client as client

def list_labels():
    gmail = client.create_client()
    results = gmail.users().labels() \
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
