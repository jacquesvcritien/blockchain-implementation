
from state import State
from helper_utils import write_to_file
from helper_utils import get_module_fn
import config as config
from block import Block
from transaction import Transaction
from txHashedContent import TxHashedContent
import json

class Protocol:
    def __init__(self, state):
        self.state = state

    #function to process a message
    def process_message_bytes(self, message, peers):

        #check command size
        if chr(message[0]) != '2':
            print("The command must start with ascii character 2")
            return

        #check last character
        if chr(message[len(message)-1]) != '3':
            print("The last character in the command must end with ascii character 3", message)
            if chr(message[3]) == "h":
                size = message[1:3]
                size = int.from_bytes(size, byteorder='big')
            return
        
        #get msg len from second and third byte
        size = message[1:3]
        size = int.from_bytes(size, byteorder='big')

        #extract command
        cmd = message[3:-1]

        #if command is longer than size
        if len(cmd) != size:
            print("The command is longer than the specified bytes", size, len(cmd), message[1:3])
            return

        #get first letter
        first_letter = chr(cmd[0])

        #if got get block count
        if first_letter == 'a':
            reply_msg = self.__handle_get_block_count()
            return [reply_msg]
        #if got block count
        if first_letter == 'c':
            reply_msg = self.__handle_block_count_response(cmd)
            return [reply_msg]
        #if got get block hashes
        elif first_letter == 'b':
            reply_msg = self.__handle_get_block_hashes()
            return [reply_msg]
        #if got get block hashes
        elif first_letter == 'h':
            reply_msgs = self.__handle_block_hashes_response(cmd)
            return reply_msgs
        #if got request block
        elif first_letter == 'r':
            reply_msg = self.__handle_request_block(cmd)
            return [reply_msg]
        #if got new block
        elif first_letter == 'z' or first_letter == 'x':
            reply_msg = self.__handle_new_block(cmd)
            return [reply_msg]
        #if got new tx
        if first_letter == 't':
            self.__handle_new_tx(cmd)
            return [None]
            # print("GOT NEW TX MSG", file=self.state.logFile)
            # self.state.logFile.flush()
            # #extract transaction number
            # trn = int.from_bytes(cmd[1:3], byteorder='big')
            # print("Got new transaction number", trn, file=self.state.logFile)
            # self.state.logFile.flush()
            # from_user = cmd[3:5].decode(config.BYTE_ENCODING_TYPE)
            # to_user = cmd[5:7].decode(config.BYTE_ENCODING_TYPE)
            # timestamp = int.from_bytes(cmd[7:11], byteorder='big')
            # approved = int.from_bytes(cmd[11:12], byteorder='big')
            # approve_tx = int.from_bytes(cmd[12:14], byteorder='big')

            # #if transaction number is more than next number, synchronise
            # if trn > len(self.state.transactions) + 1:
            #     self.state.synchronize(self, peers)
            
            # #if a new height
            # if (len(self.state.transactions)+1) == trn:
            #     #append tx
            #     new_tx = {
            #         "number": trn,
            #         "from_username": from_user,
            #         "to_username": to_user,
            #         "timestamp": timestamp,
            #         "approved": approved,
            #         "approve_tx": approve_tx
            #     }

            #     #add tx to state
            #     self.state.transactions.append(new_tx)
            #     self.state.local_tx_count += 1
            #     self.state.network_tx_count = len(self.state.transactions)
            #     #return okay
            #     return self.create_message("o".encode(config.BYTE_ENCODING_TYPE))
            # #if height already exists
            # elif len(self.state.transactions) >= trn:
            #     #if our stored tx is older, ignore this
            #     if self.state.transactions[trn-1]["timestamp"] <= timestamp:
            #         #return fail
            #         return self.create_message("f".encode(config.BYTE_ENCODING_TYPE))
            #     #if new transaction is older
            #     else:
            #         #replace
            #         self.state.transactions[trn-1] = {
            #             "number": trn,
            #             "from_username": from_user,
            #             "to_username": to_user,
            #             "timestamp": timestamp,
            #             "approved": approved,
            #             "approve_tx": approve_tx
            #         }
            #         #return ok
            #         return self.create_message("o".encode(config.BYTE_ENCODING_TYPE))


    #function to get block count from neighbours
    def get_block_count(self):
        #construct msg
        message = bytearray()
        message += "a".encode(config.BYTE_ENCODING_TYPE)
        
        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message(message)

    #function to get block hashes from neighbours
    def get_block_hashes(self):
        #construct msg
        message = bytearray()
        message += "b".encode(config.BYTE_ENCODING_TYPE)

        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message(message)

    def __empty_payload(self):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "empty_content")
        return fn() 

    #function to request block from neighbours
    def request_block(self, hash):
        #construct msg
        message = bytearray()
        message += "r".encode(config.BYTE_ENCODING_TYPE)

        #append payload to message
        message += self.__request_block_payload(hash)
        #create message
        return self.create_message(message)

    #function to create message for request block message
    def __request_block_payload(self, hash):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "request_block")
        return fn(hash)

    #function to send new block to neighbours
    def new_block(self, block):
        #construct msg
        message = bytearray()
        message += "z".encode(config.BYTE_ENCODING_TYPE)

        #append payload to message
        message += self.__block_payload(block)
        #create message
        return self.create_message(message)

    def get_highest_tx_num(self):
        return self.create_message(str.encode("h"))

    #function to create a message to be sent
    def create_message(self, message):
        #calculate message length
        msg_length = len(message)
        #switch to 2 bytes
        msg_length = msg_length.to_bytes(2, byteorder='big')

        #create message
        msg = bytearray()
        # msg += ascii(2)
        msg += ascii(2).encode(config.BYTE_ENCODING_TYPE)
        msg += msg_length
        msg += message
        msg += ascii(3).encode(config.BYTE_ENCODING_TYPE)

        # msg += ascii(3)

        return msg

    #function to create payload for send tx message
    def __tx_payload(self, block):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", config.DB_MODEL+"_tx_content")
        return fn(block)

    #function to send tx
    def send_new_tx(self, transaction):
        #prepare message to send
        new_tx_msg = bytearray()
        #add initial character
        new_tx_msg += "t".encode(config.BYTE_ENCODING_TYPE)
        #append payload to message
        new_tx_msg += self.__tx_payload(transaction)
        
        #create msg
        msg_to_send = self.create_message(new_tx_msg)
        return msg_to_send

    def send_new_tx_bytes(self, transaction):
        
        #construct transaction message
        trn = transaction["number"]
        trtime = transaction["timestamp"]
        approved = transaction["approved"]
        approve_tx = transaction["approve_tx"]

        new_tx_msg = bytearray()
        new_tx_msg += "n".encode(config.BYTE_ENCODING_TYPE)
        new_tx_msg += trn.to_bytes(2, byteorder='big')
        new_tx_msg += transaction["from_username"].encode(config.BYTE_ENCODING_TYPE)
        new_tx_msg += transaction["to_username"].encode(config.BYTE_ENCODING_TYPE)
        new_tx_msg += trtime.to_bytes(4, byteorder='big')
        new_tx_msg += approved.to_bytes(1, byteorder='big')
        new_tx_msg += approve_tx.to_bytes(2, byteorder='big')

        return self.create_message(new_tx_msg)


    def get_tx(self, trn):
        new_tx_msg = bytearray()
        new_tx_msg += "g".encode(config.BYTE_ENCODING_TYPE)
        new_tx_msg += trn.to_bytes(2, byteorder='big')
        return self.create_message(new_tx_msg)


    #function to handle get block count message
    def __handle_get_block_count(self):
        #write log
        write_to_file("GOT GET BLOCK COUNT MSG", self.state.logFile)
        
        #prepare message to return
        highest_block_res = bytearray()
        #add initial character
        highest_block_res += "c".encode(config.BYTE_ENCODING_TYPE)
        #get number of blocks
        
        block_count = self.state.get_block_count()
        #append payload to message
        highest_block_res += self.__get_block_count_res_payload(block_count)

        msg_to_send = self.create_message(highest_block_res)
        return msg_to_send

    #function to handle block count response message
    def __handle_block_count_response(self, cmd):
        #write log
        write_to_file("GOT BLOCK COUNT RESPONSE MSG", self.state.logFile)

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_block_count_message")
        #get block count
        block_count_received = fn(cmd)

        #if block count received is bigger than local block count
        if block_count_received > self.state.local_block_count:
            self.state.network_block_count = block_count_received
            #prepare message to get block hashes
            get_block_hashes_msg = self.get_block_hashes()
            return get_block_hashes_msg

        return None

    #function to create message for block count return
    def __get_block_count_res_payload(self, block_count):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "get_block_count_res")
        return fn(block_count)

    #function to handle get block hashes message
    def __handle_get_block_hashes(self):
        #write log
        write_to_file("GOT GET BLOCK HASHES MSG", self.state.logFile)
        
        #prepare message to return
        block_hashes_res = bytearray()
        #add initial character
        block_hashes_res += "h".encode(config.BYTE_ENCODING_TYPE)
        #get block hashes
        hashes = self.state.get_block_hashes()
        #append payload to message
        block_hashes_res += self.__get_block_hashes_res_payload(hashes)

        msg_to_send = self.create_message(block_hashes_res)
        return msg_to_send

    #function to create message for block hashes return
    def __get_block_hashes_res_payload(self, hashes):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "get_block_hashes_res")
        return fn(hashes)

    #function to handle block hashes response message
    def __handle_block_hashes_response(self, cmd):
        #write log
        write_to_file("GOT BLOCK HASHES RESPONSE MSG", self.state.logFile)

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_block_hashes_message")
        #get block hashes
        received_hashes = fn(cmd)

        #init messages to send
        messages_to_send = []

        #if number of block hashes received is bigger than local block count
        if len(received_hashes) > self.state.local_block_count:
            index = 1
            #for each hash
            for hash in received_hashes:
                #if block hash does not match our block hash, request block
                if self.state.chain.get_block_hash(index) != hash:
                    # print("Requesting hash", hash)
                    messages_to_send.append(self.request_block(hash))

                #increment counter
                index += 1

        return messages_to_send

    #function to handle request block message
    def __handle_request_block(self, cmd):
        #write log
        write_to_file("GOT REQUEST BLOCK MSG", self.state.logFile)

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_request_block_message")
        #get block hash
        received_hash = fn(cmd)
        
        #prepare message to return
        request_block_res = bytearray()
        #add initial character
        request_block_res += "x".encode(config.BYTE_ENCODING_TYPE)
        #get block hashes
        block = self.state.get_block(received_hash)
        #append payload to message
        request_block_res += self.__block_payload(block)

        msg_to_send = self.create_message(request_block_res)
        return msg_to_send

    #function to create message for request block return
    def __block_payload(self, block):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "block_content")
        return fn(block)

    #function to send a block
    def send_block(self, letter, block):
        #prepare message to send
        block_msg = bytearray()
        #add initial character
        block_msg += letter.encode(config.BYTE_ENCODING_TYPE)
        #append payload to message
        block_msg += self.__block_payload(block)
        
        #create msg
        msg_to_send = self.create_message(block_msg)
        return msg_to_send

    #function to handle new block message
    def __handle_new_block(self, cmd):
        #write log
        write_to_file("GOT NEW BLOCK MSG", self.state.logFile)

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_new_block_message")
        #get block hashes
        payload_received = fn(cmd)

        #check if previous hash of new block does not match current head hash
        new_block_prev_hash = payload_received["hashedContent"]["prev_hash"]
        #get block with the same prev hash
        our_block, our_index = self.state.chain.get_block_with_prev_hash(new_block_prev_hash)

        #this is a flag which holds whether the received block is older than our block with the same prev hash
        older_block = False

        #if not a new block
        if our_index != -1:
            #if new hash does not match, check if received block is older
            if payload_received["hash"] != our_block.hash:
                #if our block is older, hence the original
                if our_block.hashed_content.timestamp < payload_received["hashedContent"]["timestamp"]:
                    print("We found an older block on our chain with the same previous hash", new_block_prev_hash)
                    #send our block to the chain
                    return self.send_block("x", our_block)
                #otherwise we need to verify
                else:
                    older_block = True
                    print("Need to check hash", payload_received["hash"])

        #if it is a completely new block or an older block which needs to be verified
        if older_block or our_block == None:
            #initialise block
            block = Block.load(payload_received["hashedContent"], payload_received["hash"])
            #verify block
            verified = block.verify(self.state.database)

            #if not verified
            if not verified:
                print("Block not verified", payload_received["hashedContent"], payload_received["hash"])
                return

            #perform block transfers
            self.state.perform_transfers(block)

            #if is a completely new block
            if our_index == -1:
                #add block to chain
                self.state.insert_block(block)
            #otherwise we need to replace the block with the same previous hash at the index obtained
            else:
                print("Replacing block with hash", block.hash)
                self.state.chain.replace_block(index, block)

        return None

    #function to handle new transaction message
    def __handle_new_tx(self, cmd):
        write_to_file("GOT NEW TX MSG", self.state.logFile)

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_"+config.DB_MODEL+"_transaction")
        payload_received = fn(cmd)

        #initialise transaction
        spent_tx = None if config.DB_MODEL == "account" else payload_received["hashedContent"]["spent_tx"]
        hashed_content = TxHashedContent.load(payload_received["hashedContent"]["from_ac"], payload_received["hashedContent"]["to_ac"], payload_received["hashedContent"]["signature"], spent_tx)
        tx = Transaction.load(hashed_content, payload_received["hash"])

        #verify tx
        verified = tx.verify()

        #if tx cannot be verified
        if not verified:
            print("TX Hash failed to be verified")
            return

        #check if transfer can happen
        transfer_allowed=self.state.database.check_transfer(tx, False)

        if not transfer_allowed:
            print("TX Transfer not allowed - sender out of funds")
            return
            
        #append tx to txs pool
        self.state.transactions.append(tx)


