from helper_utils import write_to_file
import config as config
import json

#function to create JSON message for block count return
def get_block_count_res(block_count):
    #create payload
    payload = {
        "blocks": block_count
    }
    payload = json.dumps(payload)
    return payload.encode(config.BYTE_ENCODING_TYPE)

#function to create JSON message for block hashes return
def get_block_hashes_res(hashes):
    payload = {
        "hashes": hashes
    }
    payload = json.dumps(payload)
    return payload.encode(config.BYTE_ENCODING_TYPE)

#function to create JSON message for request block
def request_block(hash):
    payload = {
        "hash": hash
    }
    payload = json.dumps(payload)
    return payload.encode(config.BYTE_ENCODING_TYPE)

#function to create JSON message for block message
def block_content(block):
    payload = {
        "block": {
            "hash": block.hash,
            "hashedContent": block.hashed_content.get_hashed_content()
        }
    }
    payload = json.dumps(payload)
    return payload.encode(config.BYTE_ENCODING_TYPE)

#function to create empty JSON message
def empty_content():
    return json.dumps(None)


#function to handle block count response message
def handle_block_count_message(cmd):
    #change to json
    payload_received = json.loads(cmd[1:len(cmd)])

    #get block count
    return payload_received["blocks"]

#function to handle block hashes response message
def handle_block_hashes_message(cmd):
    #change to json
    payload_received = json.loads(cmd[1:len(cmd)])

    #get block hashes
    return payload_received["hashes"]

#function to handle request block message
def handle_request_block_message(cmd):
    #change to json
    payload_received = json.loads(cmd[1:len(cmd)])
    #get hash
    return payload_received["hash"]
    
#function to handle new block message
def handle_new_block_message(cmd):
    #change to json
    return json.loads(cmd[1:len(cmd)])["block"]

#function to create JSON message for tx message
def tx_content(tx):
    payload = {
        "transaction": {
            "hash": tx.hash,
            "hashedContent": tx.hashed_content.get_hashed_content()
        }
    }
    payload = json.dumps(payload)
    return payload.encode(config.BYTE_ENCODING_TYPE)

#function to handle a json encoded transaction using the account model
def handle_account_transaction(cmd):
    #change to json
    payload_received = json.loads(cmd[1:len(cmd)])["transaction"]
    print("received new transaction", payload_received)

    return payload_received

