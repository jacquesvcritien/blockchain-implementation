import json

#function to create JSON message for block count return
def get_block_count_res(block_count):
    #create payload
    payload = {
        "blocks": block_count
    }
    return json.dumps(payload)

#function to create JSON message for block hashes return
def get_block_hashes_res(hashes):
    payload = {
        "hashes": hashes
    }
    return json.dumps(payload)

#function to create JSON message for request block
def request_block(hash):
    payload = {
        "hash": hash
    }
    return json.dumps(payload)

#function to create JSON message for block message
def block_content(block):
    payload = {
        "block": {
            "hash": block.hash,
            "hashedContent": block.hashed_content.get_hashed_content()
        }
    }
    return json.dumps(payload)

#function to create empty JSON message
def empty_content():
    return json.dumps(None)