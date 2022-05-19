import math
from helper_utils import write_to_file
import config as config

#function to create BYTE message for block count return
def get_block_count_res(block_count):
    msg_to_send = bytearray()
    msg_to_send += block_count.to_bytes(3, byteorder='big')
    return msg_to_send

#function to create BYTE message for block hashes return
def get_block_hashes_res(hashes):
    #get hashes length
    hashes_len = len(hashes)

    #prepare message to send
    msg_to_send = bytearray()
    #append number of hashes
    msg_to_send += hashes_len.to_bytes(3, byteorder="big")

    #for every hash
    for hash in hashes:
        #add hash
        msg_to_send += hash.encode(config.BYTE_ENCODING_TYPE)
        
    return msg_to_send

#function to create BYTE message for request block
def request_block(hash):
    return hash.encode(config.BYTE_ENCODING_TYPE)

#function to get bytes needed for a number
def bytes_needed_for_txs_len(txs_len):
    return max(1, math.ceil(math.ceil(math.log(txs_len,2))/8))

#function to create BYTE message for block message
def block_content(block):
    #init message to send
    msg_to_send = bytearray()
    #append hash
    msg_to_send += block.hash.encode(config.BYTE_ENCODING_TYPE)
    #append previous hash
    msg_to_send += block.hashed_content.prev_hash.encode(config.BYTE_ENCODING_TYPE)
    #append nonce - 5 bytes
    msg_to_send += block.hashed_content.nonce.to_bytes(5, byteorder="big")
    #append timestamp - 6 bytes
    msg_to_send += block.hashed_content.timestamp.to_bytes(6, byteorder="big")
    #append number of bytes needed for tx length
    txs_len = len(block.hashed_content.transactions)
    bytes_needed_for_txs = bytes_needed_for_txs_len(txs_len)
    msg_to_send += bytes_needed_for_txs.to_bytes(1, byteorder="big")
    #append number of txs
    msg_to_send += txs_len.to_bytes(bytes_needed_for_txs, byteorder="big")

    #for each transaction
    for tx in block.hashed_content.transactions:
        #add tx's hash
        msg_to_send += tx.hash.encode(config.BYTE_ENCODING_TYPE)
        #add tx's sender
        msg_to_send += tx.hashed_content.signed_content.from_ac.encode(config.BYTE_ENCODING_TYPE)
        #add txs's receiver
        msg_to_send += tx.hashed_content.signed_content.to_ac.encode(config.BYTE_ENCODING_TYPE)

        #add tx's signature
        msg_to_send += tx.hashed_content.signature.encode(config.BYTE_ENCODING_TYPE)

        #if config is utxo model
        if(config.DB_MODEL == "utxo"):
            #add spent tx
            msg_to_send += tx.hashed_content.spent_tx.to_bytes(5, byteorder="big")


    return msg_to_send

#function to create empty BYTE message
def empty_content():
    return ""

#function to handle block count response message
def handle_block_count_message(cmd):
    return int.from_bytes(cmd[1:len(cmd)], byteorder='big')


#function to handle block hashes response message
def handle_block_hashes_message(cmd):

    #get number of hashes
    hashes_len = int.from_bytes(cmd[1:4], byteorder="big")

    #hashes array to populate
    hashes = []
    #get each hash and add it to an array
    for i in range(4, len(cmd), 64):
        end_index = i + 64
        #get hash bytes 
        hash = cmd[i:end_index].decode(config.BYTE_ENCODING_TYPE)
        #append hash to hashes
        hashes.append(hash)

    #return block hashes
    return hashes


#function to handle request block message
def handle_request_block_message(cmd):
    #get hash from message
    return cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)

#function to handle new block message
def handle_new_block_message(cmd):

    #start index to obtain
    start_index = 1
    #end index to obtain
    end_index = 65
    #block to populate
    block = {
        "hash": "",
        "hashedContent": {
            "nonce": -1,
            "prev_hash": "",
            "timestamp": -1,
            "transactions": []
        }
    }
    #get block hash
    block["hash"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get previous block hash
    start_index = end_index
    end_index += 64
    block["hashedContent"]["prev_hash"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get nonce
    start_index = end_index
    end_index += 5
    block["hashedContent"]["nonce"] = int.from_bytes(cmd[start_index:end_index], byteorder='big')
    #get timestamp
    start_index = end_index
    end_index += 6
    block["hashedContent"]["timestamp"] = int.from_bytes(cmd[start_index:end_index], byteorder='big')
    #get tx len bytes
    start_index = end_index
    end_index += 1
    bytes_to_read = int.from_bytes(cmd[start_index:end_index], byteorder='big')
    #get tx count
    start_index = end_index
    end_index += bytes_to_read
    transactions_count = int.from_bytes(cmd[start_index:end_index], byteorder='big')

    #for each transaction
    for i in range(transactions_count):
        tx = {
            "hash": "",
            "hashedContent": {
                "from_ac": "",
                "to_ac": "",
                "signature": ""
            }
        }

        #get transaction hash
        start_index = end_index
        end_index += 64
        tx["hash"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
        #get tx's sender
        start_index = end_index
        end_index += 128
        tx["hashedContent"]["from_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
        #get tx's receiver
        start_index = end_index
        end_index += 128
        tx["hashedContent"]["to_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
        #get tx's signature
        start_index = end_index
        end_index += 128
        tx["hashedContent"]["signature"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)

        #if config is utxo model
        if(config.DB_MODEL == "utxo"):
            #get spent tx
            start_index = end_index
            end_index += 5
            tx["hashedContent"]["spent_tx"] = int.from_bytes(cmd[start_index:end_index], byteorder='big')


        #append tx
        block["hashedContent"]["transactions"].append(tx)

    #change to json
    return block

#function to create bytes message for account model tx message
def account_tx_content(tx):
    #init message to send
    msg_to_send = bytearray()
    #append hash
    msg_to_send += tx.hash.encode(config.BYTE_ENCODING_TYPE)
    #append sender
    msg_to_send += tx.hashed_content.signed_content.from_ac.encode(config.BYTE_ENCODING_TYPE)
    #append receiver
    msg_to_send += tx.hashed_content.signed_content.to_ac.encode(config.BYTE_ENCODING_TYPE)
    #append signature
    msg_to_send += tx.hashed_content.signature.encode(config.BYTE_ENCODING_TYPE)
    
    return msg_to_send

#function to create bytes message for utxo model tx message
def utxo_tx_content(tx):
    #init message to send
    msg_to_send = bytearray()
    #append hash
    msg_to_send += tx.hash.encode(config.BYTE_ENCODING_TYPE)
    #append sender
    msg_to_send += tx.hashed_content.signed_content.from_ac.encode(config.BYTE_ENCODING_TYPE)
    #append receiver
    msg_to_send += tx.hashed_content.signed_content.to_ac.encode(config.BYTE_ENCODING_TYPE)
    #append signature
    msg_to_send += tx.hashed_content.signature.encode(config.BYTE_ENCODING_TYPE)
    #append spent_tx
    msg_to_send += tx.hashed_content.spent_tx.to_bytes(5, byteorder="big")
    
    return msg_to_send

#function to handle a byte encoded transaction using the account model
def handle_account_transaction(cmd):
    #start index to obtain
    start_index = 1
    #end index to obtain
    end_index = 65
    #tx to populate
    tx = {
        "hash": "",
        "hashedContent": {
            "from_ac": "",
            "to_ac": "",
            "signature": ""
        }
    }
    #get tx hash
    tx["hash"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get sender
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["from_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get receiver
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["to_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get signature
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["signature"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)

    return tx

#function to handle a byte encoded transaction using the utxo model
def handle_utxo_transaction(cmd):
    #start index to obtain
    start_index = 1
    #end index to obtain
    end_index = 65
    #tx to populate
    tx = {
        "hash": "",
        "hashedContent": {
            "from_ac": "",
            "to_ac": "",
            "signature": ""
        }
    }
    #get tx hash
    tx["hash"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get sender
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["from_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get receiver
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["to_ac"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get signature
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["signature"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get signature
    start_index = end_index
    end_index += 128
    tx["hashedContent"]["signature"] = cmd[start_index:end_index].decode(config.BYTE_ENCODING_TYPE)
    #get spent_tx
    start_index = end_index
    end_index += 5
    tx["hashedContent"]["signature"] = int.from_bytes(cmd[start_index:end_index], byteorder='big')


    return tx