
from state import State
from helper_utils import write_to_file
from helper_utils import get_module_fn
import config as config
import json

class Protocol:
    def __init__(self, state):
        self.state = state

    #function to process a message
    def process_message_bytes(self, message, peers):

        #check command size
        if message[0] != ascii(2):
            print("The command must start with ascii character 2")
            return

        #check last character
        if message[len(message)-1] != ascii(3):
            print("The last character in the command must end with ascii character 3")
            return
        
        #get msg len from second and third byte
        size = message[1:3]

        #extract command
        cmd = message[3:-1]

        #if command is longer than size
        if len(cmd) != size:
            print("The command is longer than the specified bytes")
            return

        #get first letter
        first_letter = chr(message[2])

        #if got get block count
        if first_letter == 'a':
            reply_msg = __handle_get_block_count()
            return reply_msg
        #if got block count
        if first_letter == 'c':
            reply_msg = __handle_block_count_response(cmd)
            return reply_msg
        #if got get block hashes
        elif first_letter == 'b':
            reply_msg = __handle_get_block_hashes()
            return reply_msg
        #if got get block hashes
        elif first_letter == 'h':
            reply_msg = __handle_block_hashes_response(cmd)
            return reply_msg
        #if got request block
        elif first_letter == 'r':
            reply_msg = __handle_request_block(cmd)
            return reply_msg
        #if got new block
        elif first_letter == 'z':
            reply_msg = __handle_new_block(cmd)
            return reply_msg
        #if got new tx
        if first_letter == 'n':
            print("GOT NEW TX MSG", file=self.state.logFile)
            self.state.logFile.flush()
            #extract transaction number
            trn = int.from_bytes(cmd[1:3], byteorder='big')
            print("Got new transaction number", trn, file=self.state.logFile)
            self.state.logFile.flush()
            from_user = cmd[3:5].decode(config.BYTE_ENCODING_TYPE)
            to_user = cmd[5:7].decode(config.BYTE_ENCODING_TYPE)
            timestamp = int.from_bytes(cmd[7:11], byteorder='big')
            approved = int.from_bytes(cmd[11:12], byteorder='big')
            approve_tx = int.from_bytes(cmd[12:14], byteorder='big')

            #if transaction number is more than next number, synchronise
            if trn > len(self.state.transactions) + 1:
                self.state.synchronize(self, peers)
            
            #if a new height
            if (len(self.state.transactions)+1) == trn:
                #append tx
                new_tx = {
                    "number": trn,
                    "from_username": from_user,
                    "to_username": to_user,
                    "timestamp": timestamp,
                    "approved": approved,
                    "approve_tx": approve_tx
                }

                #add tx to state
                self.state.transactions.append(new_tx)
                self.state.local_tx_count += 1
                self.state.network_tx_count = len(self.state.transactions)
                #return okay
                return self.create_message_bytes("o".encode(config.BYTE_ENCODING_TYPE))
            #if height already exists
            elif len(self.state.transactions) >= trn:
                #if our stored tx is older, ignore this
                if self.state.transactions[trn-1]["timestamp"] <= timestamp:
                    #return fail
                    return self.create_message_bytes("f".encode(config.BYTE_ENCODING_TYPE))
                #if new transaction is older
                else:
                    #replace
                    self.state.transactions[trn-1] = {
                        "number": trn,
                        "from_username": from_user,
                        "to_username": to_user,
                        "timestamp": timestamp,
                        "approved": approved,
                        "approve_tx": approve_tx
                    }
                    #return ok
                    return self.create_message_bytes("o".encode(config.BYTE_ENCODING_TYPE))


    #function to get block count from neighbours
    def get_block_count(self):
        #construct msg
        message = bytearray()
        message += "a".encode(config.BYTE_ENCODING_TYPE)
        
        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message_bytes(message)

    #function to get block hashes from neighbours
    def get_block_hashes(self):
        #construct msg
        message = bytearray()
        message += "b".encode(config.BYTE_ENCODING_TYPE)

        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message_bytes(message)

    def __empty_payload(self):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "empty_content")
        return fn() 

    #function to request block from neighbours
    def request_block(self, hash):
        #construct msg
        message = bytearray()
        message += "r".encode(config.BYTE_ENCODING_TYPE)

        #get payload
        payload = self.__request_block_payload(hash)
        #append payload to message
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message_bytes(message)

    #function to create message for request block message
    def __request_block_payload(hash):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "request_block")
        return fn(hash)

    #function to send new block to neighbours
    def new_block(self, block):
        #construct msg
        message = bytearray()
        message += "z".encode(config.BYTE_ENCODING_TYPE)

        #get payload
        payload = self.__block_payload(block)
        #append payload to message
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message_bytes(message)

    def get_highest_tx_num(self):
        return self.create_message_bytes(str.encode("h"))

    #function to create a message to be sent
    def create_message_bytes(self, message):
        #calculate message length
        msg_length = len(message)
        #switch to 2 bytes
        msg_length = msg_length.to_bytes(2, byteorder='big')

        #create message
        msg = bytearray()
        msg += ascii(2).encode(config.BYTE_ENCODING_TYPE)
        msg += msg_length
        msg += message
        msg += ascii(3).encode(config.BYTE_ENCODING_TYPE)

        return msg

    def send_new_tx(self, transaction):
        #construct transaction message
        trn = str(transaction["number"])[2:len(message)]
        trtime = str(transaction["timestamp"])[2:len(message)]
        new_tx_msg = "n" + trn + transaction["from_username"] + transaction["to_username"] + trtime
        return create_message(new_tx_msg)

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

        return self.create_message_bytes(new_tx_msg)


    def get_tx(self, trn):
        new_tx_msg = bytearray()
        new_tx_msg += "g".encode(config.BYTE_ENCODING_TYPE)
        new_tx_msg += trn.to_bytes(2, byteorder='big')
        return self.create_message_bytes(new_tx_msg)


    #function to handle get block count message
    def __handle_get_block_count(self):
        #write log
        write_to_file("GOT GET BLOCK COUNT MSG", self.state.logFile)
        
        #prepare message to return
        highest_block_res = bytearray()
        #add initial character
        highest_block_res += "c".encode(config.BYTE_ENCODING_TYPE)
        #get number of blocks
        block_count = state.get_block_count()
        #get payload
        payload = self.__get_block_count_res_payload(block_count)
        #append payload to message
        highest_block_res += payload.encode(config.BYTE_ENCODING_TYPE)

        msg_to_send = self.create_message_bytes(highest_block_res)
        return msg_to_send

    #function to handle block count response message
    def __handle_block_count_response(self, cmd):
        #write log
        write_to_file("GOT BLOCK COUNT RESPONSE MSG", self.state.logFile)

        payload_received = cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)
        #change to json
        payload_received = json.load(payload_received)

        #get blockc ount
        self.state.local_block_count = payload_received["blocks"]

        #if block count received is bigger than local block count
        if block_count > self.state.local_block_count:
            self.state.network_block_count = block_count
            #prepare message to get block hashes
            get_block_hashes_msg = self.get_block_hashes()
            return get_block_hashes_msg

        return None

    #function to create JSON message for block count return
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
        hashes = state.get_block_hashes()
        #get payload
        payload = self.__get_block_hashes_res_payload(hashes)
        #append payload to message
        block_hashes_res += payload.encode(config.BYTE_ENCODING_TYPE)

        msg_to_send = self.create_message_bytes(block_hashes_res)
        return msg_to_send

    #function to create JSON message for block hashes return
    def __get_block_hashes_res_payload(self, hashes):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "get_block_hashes_res")
        return fn(hashes)

    #function to handle block hashes response message
    def __handle_block_hashes_response(self, cmd):
        #write log
        write_to_file("GOT BLOCK HASHES RESPONSE MSG", self.state.logFile)

        payload_received = cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)
        #change to json
        payload_received = json.load(payload_received)

        #get blockc ount
        self.state.local_block_count = payload_received["blocks"]

        #if block count received is bigger than local block count
        if block_count > self.state.local_block_count:
            self.state.network_block_count = block_count
            #prepare message to get block hashes
            get_block_hashes_msg = self.get_block_hashes()
            return get_block_hashes_msg

        return None

    #function to handle request block message
    def __handle_request_block(self, cmd):
        #write log
        write_to_file("GOT REQUEST BLOCK MSG", self.state.logFile)

        payload_received = cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)
        print("received_payload", payload_received)
        #change to json
        payload_received = json.load(payload_received)
        #get hash
        hash = payload_received["hash"]
        
        #prepare message to return
        request_block_res = bytearray()
        #add initial character
        request_block_res += "b".encode(config.BYTE_ENCODING_TYPE)
        #get block hashes
        block = state.get_block(hash)
        #get payload
        payload = self.__block_payload(block)
        #append payload to message
        request_block_res += payload.encode(config.BYTE_ENCODING_TYPE)

        msg_to_send = self.create_message_bytes(request_block_res)
        return msg_to_send

    #function to create JSON message for request block return
    def __block_payload(self, block):
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "block_content")
        return fn(block)

    #function to handle new block message
    def __handle_new_block(self, cmd):
        #write log
        write_to_file("GOT NEW BLOCK MSG", self.state.logFile)

        payload_received = cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)
        print("received new block", payload_received)
        #change to json
        payload_received = json.load(payload_received)

        #initialise block
        block = Block.load(payload_received["hashedContent"], payload_received["hash"])
        #verify block
        verified = block.verify()

        #if not verified
        if not verified:
            print("Block not verified", payload_received["hashedContent"], payload_received["hash"])
            return

        #perform block transfers
        self.state.perform_transfers(block)

        #add block to chain
        self.state.chain.add_block(block)

    #function to handle new transaction message
    def __handle_new_tx(self, cmd):
        #get function from module
        fn = get_module_fn("models."+config.DB_MODEL+".tx_handler", "handle_"+config.PAYLOAD_ENCODING+"_encoded_transaction")
        return fn(block)


