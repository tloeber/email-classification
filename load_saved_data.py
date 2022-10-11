import pickle 
with open('msgs_replied_to.pickle', 'rb') as f:
    msgs_repiled_to = pickle.load(f)
    print(msgs_repiled_to)

with open('msgs_to_discard.pickle', 'rb') as f:
    msgs_to_discard = pickle.load(f)
    print(msgs_to_discard)