
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
        """
        Class initialiser

        :param state: a reference to the initialised state
        """

        self.state = state

    def process_message(self, message, peers, sender_ip, sender_port):
        """
        Function to process a message

        :param message: the message sent
        :param peers: a reference to peers
        :param sender_ip: the sender's ip
        :param sender_port: the sender's port

        :return: list of messages to broadcast to peers
        """

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
            reply_msgs = self.__handle_new_block(cmd, first_letter == 'z')
            return reply_msgs
        #if got new tx
        if first_letter == 't':
            self.__handle_new_tx(cmd)
            return [None]
        #if got new public key
        if first_letter == 'd':
            pk = self.__handle_pk(cmd)
            peers.received_peer_ping(pk)
            peers.add_pk_to_peer(sender_ip, sender_port, pk)
            return [None]


    def get_block_count(self):
        """
        Function to get block count from neighbours

        :return: message to send to peers to get block count
        """

        #construct msg
        message = bytearray()
        message += "a".encode(config.BYTE_ENCODING_TYPE)
        
        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message(message)

    def get_block_hashes(self):
        """
        Function to get block hashes from neighbours

        :return: message to send to peers
        """
        #construct msg
        message = bytearray()
        message += "b".encode(config.BYTE_ENCODING_TYPE)

        #get payload
        payload = self.__empty_payload()
        message += payload.encode(config.BYTE_ENCODING_TYPE)
        #create message
        return self.create_message(message)

    def __empty_payload(self):
        """
        Function to send emoty payload

        :return: message to send to peers
        """

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "empty_content")
        return fn() 

    def request_block(self, hash):
        """
        Function to request block from peers 

        :param hash: the hash of the block to obtain

        :return: message to send to peers
        """

        #construct msg
        message = bytearray()
        message += "r".encode(config.BYTE_ENCODING_TYPE)

        #append payload to message
        message += self.__request_block_payload(hash)
        #create message
        return self.create_message(message)

    def __request_block_payload(self, hash):
        """
        Function to create message for request block message

        :param hash: the hash of the block to obtain

        :return: payload for request block message
        """

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "request_block")
        return fn(hash)

    def new_block(self, block):
        """
        Function to send new block to neighbours

        :param block: new block to send

        :return: message to send to peers
        """

        #construct msg
        message = bytearray()
        message += "z".encode(config.BYTE_ENCODING_TYPE)

        #append payload to message
        message += self.__block_payload(block)
        #create message
        return self.create_message(message)

    def create_message(self, message):
        """
        Function to create a message to be sent

        :param message: message to send

        :return: message to send to peers
        """

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

    def __tx_payload(self, transaction):
        """
        Function to create payload for send tx message

        :param transaction: transaction to send

        :return: the payload to send 
        """

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", config.DB_MODEL+"_tx_content")
        return fn(transaction)

    def send_new_tx(self, transaction):
        """
        Function to create message to send a transaction

        :param transaction: transaction to send

        :return: message to send to peers
        """

        #prepare message to send
        new_tx_msg = bytearray()
        #add initial character
        new_tx_msg += "t".encode(config.BYTE_ENCODING_TYPE)
        #append payload to message
        new_tx_msg += self.__tx_payload(transaction)
        
        #create msg
        msg_to_send = self.create_message(new_tx_msg)
        return msg_to_send

    def get_peers_pks(self):
        """
        Function to get peers' public keys

        :return: message to send to peers
        """

        #prepare message to return
        msg_to_send = bytearray()
        #add initial character
        msg_to_send += "d".encode(config.BYTE_ENCODING_TYPE)
        #get public key
        public_key = self.state.public_key
        #append payload to message
        msg_to_send += self.__discover_payload(public_key)
        msg_to_send = self.create_message(msg_to_send)
        return msg_to_send

    def __handle_get_block_count(self):
        """
        Function to handle get block count message

        :return: message to send to peers
        """

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

    def __handle_block_count_response(self, cmd):
        """
        Function to handle block count response message

        :return: message to send to peers
        """

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

    def __get_block_count_res_payload(self, block_count):
        """
        Function to get payload for a get block count message 

        :return: payload for a get block count message 
        """
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "get_block_count_res")
        return fn(block_count)

    def __handle_get_block_hashes(self):
        """
        Function to handle get block hashes message

        :return: message to send to peers
        """

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

    def __get_block_hashes_res_payload(self, hashes):
        """
        Function to get payload for a get block hashes message 

        :return: payload for a get block count message 
        """
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "get_block_hashes_res")
        return fn(hashes)

    def __handle_block_hashes_response(self, cmd):
        """
        Function to handle get block hashes message response

        :return: message to send to peers
        """

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
            print(received_hashes)
            for hash in received_hashes:
                #if block hash does not match our block hash, request block
                if self.state.chain.get_block_hash(index) != hash:
                    # print("Requesting hash", hash)
                    print("Requesting block", index, self.state.chain.get_block_hash(index))
                    messages_to_send.append(self.request_block(hash))

                #increment counter
                index += 1

        return messages_to_send

    def __handle_request_block(self, cmd):
        """
        Function to handle request block message

        :return: message to send to peers
        """
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

    def __block_payload(self, block):
        """
        Function to create payload for request block message

        :return: payload for request block message
        """

        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "block_content")
        return fn(block)

    def send_block(self, letter, block):
        """
        Function to send a block message

        :return: message to send to peers
        """

        #prepare message to send
        block_msg = bytearray()
        #add initial character
        block_msg += letter.encode(config.BYTE_ENCODING_TYPE)
        #append payload to message
        block_msg += self.__block_payload(block)
        
        #create msg
        msg_to_send = self.create_message(block_msg)
        return msg_to_send

    def __handle_new_block(self, cmd, new_block):
        """
        Function to handle new block message

        :return: message to send to peers
        """
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
        #check if new block prev hash is the last has in our chain
        prev_hash_last_block = self.state.chain.is_hash_last_block(new_block_prev_hash)
        
        replace_block = False

        #initialise block
        block = Block.load(payload_received["hashedContent"], payload_received["hash"])
        
        #if not a new block
        if (not new_block or our_index != -1) and not prev_hash_last_block:
            #get function from module
            handle_old_block = get_module_fn("miners."+config.MINING_TYPE+"_miner", "handle_old_block")
            #this is a flag which holds whether the received block should be replacing our block
            replace_block, msg = handle_old_block(self, block, our_block, our_index, payload_received, new_block_prev_hash)
            if replace_block:
                print("Should replace block")

            #if a message needs to be sent
            if msg != None:
                return msg

        #if it is a completely new block or an older block which needs to be verified
        if replace_block or new_block or prev_hash_last_block:
            #verify block
            verified = block.verify(self.state.database, new_block)

            #if not verified
            if not verified:
                print("Block not verified", payload_received["hashedContent"], payload_received["hash"])
                return [False]

            #if is a completely new block
            if (new_block or prev_hash_last_block) and our_index == -1:
                #add block to chain
                self.state.insert_block(block)
            #otherwise we need to replace the block with the same previous hash at the index obtained
            else:
                # first we need to check if the block transfers were possible in that past block
                transfers_acceptable = self.state.perform_check_transfers_past_block(block, our_index)   
                self.state.chain.replace_block(our_index, block, self.state.database)
                #perform block transfers
                self.state.perform_transfers(block)
                #reset mining tables
                self.state.database.reset_mining_tables()

                #reset counts
                self.state.local_block_count = len(self.state.chain.blocks)
                self.state.network_block_count = len(self.state.chain.blocks)

        return [None]

    def __handle_new_tx(self, cmd):
        """
        Function to handle new transaction message

        :return: message to send to peers
        """

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

        #make transfer to mining table
        self.state.database.transfer(tx, False)
            
        #append tx to txs pool
        self.state.add_pending_tx(tx)

    def __discover_payload(self, transaction):
        """
        Function to create payload for a discover message

        :return: payload for a discover message
        """
        #get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "discover_content")
        return fn(transaction)

    def __handle_pk(self, cmd):
        """
        Function to handle new public key message

        :return: public key
        """

        write_to_file("GOT PK MSG", self.state.logFile)

        ##get function from module
        fn = get_module_fn("encoding."+config.PAYLOAD_ENCODING+"_encoding", "handle_pk_msg")
        #get public_key
        received_pk = fn(cmd)

        return received_pk
