from datetime import datetime
import config as config
import time
import json
from helper_utils import get_module_fn
from helper_utils import write_to_file

class State:
    def __init__(self, ip, port, chain):
        """
        Class initialiser

        :param ip: the ip listening on
        :param port: the port listening on
        :param chain: reference to the initialised chain
        """
        
        self.user_initials = ""
        self.transactions = []
        self.chain = chain
        self.local_block_count = 0
        self.network_block_count = 0
        #read username
        self.read_username()
        self.ip = ip
        self.port = port

        #init database
        Database = get_module_fn("models."+config.DB_MODEL+".db_model", "Database")

        #if traverse chain version
        if config.DB_MODEL == "utxo" and config.TRAVERSE_UTXO == "chain":
            Database = get_module_fn("models."+config.DB_MODEL+".db_model_traverse", "Database")
            self.database = Database(self.chain, self.transactions)
        else:
            self.database = Database(port)

        self.logFile = open('logs/log_'+str(port)+'.txt', 'w')

    def synchronize(self, protocol, peers):
        """ 
        Function synchronise

        :param protocol: protocol used
        :param peers: peers to synchronise with
        """

        get_blocks_count_msg = protocol.get_block_count()
        peers.broadcast_message(get_blocks_count_msg)

        write_to_file("Syncing and asking for block count", self.logFile)

        peers_pks_msg = protocol.get_peers_pks()
        peers.broadcast_message(peers_pks_msg)

    def read_username(self):
        """ 
        Function to read username
        """

        #keep reading input until its valid 
        while len(self.user_initials) != 2:
            self.user_initials = input("Enter your username: ").upper()
            if len(self.user_initials) != 2:
                print("Username must be the initials (2 characters long)")

        print("Logged in as "+self.user_initials)

    def get_transaction(self, trn):
        """ 
        Function to read a transaction

        :param trn: index of transaction

        :return: the transaction at the given index
        """
        return self.transactions[trn-1]

    def get_block_count(self):
        """ 
        Function to get block count

        :return: the number of blocks in chain
        """

        #if there are no blocks
        if len(self.chain.blocks) == 0:
            return 0

        return len(self.chain.blocks)

    def get_block(self, hash):
        """ 
        Function to get the block by hash

        :param hash: the hash to get

        :return: the block with the given hash
        """
        #loop through each block
        for block in self.chain.blocks:
            #if block matches, return hash
            if(block.hash == hash):
                return block

        return None

    def get_block_hashes(self):
        """ 
        Function to get the block hashes

        :return: block hashes from the chain
        """
        block_hashes = []

        #loop through blocks
        for block in self.chain.blocks:
            #append hash
            block_hashes.append(block.hash)

        return block_hashes

    def get_latest_hash(self):
        """ 
        Function to get latest hash

        :return: latest hash
        """

        return self.chain.blocks[-1].hash if len(self.chain.blocks) > 0 else "0"

    def insert_block(self, block):
        """ 
        Function to insert block

        :param block: block to insert
        """

        #increment local count
        self.local_block_count += 1
        self.transactions.clear()

        #if local block count is more than network, increase network
        if(self.local_block_count > self.network_block_count):
            self.network_block_count = self.local_block_count

        #check if there exists a block with same previous hash
        #get block with the same prev hash
        our_block, our_index = self.chain.get_block_with_prev_hash(block.hashed_content.prev_hash)

        #if we have no block
        if our_index == -1:
            #add block to chain
            self.chain.add_block(block)
        else:
            transfers_acceptable = self.perform_check_transfers_past_block(block, our_index)   
            self.chain.replace_block(our_index, block, self.database)

        #perform transfers
        self.perform_transfers(block)

        #reset mining balances
        self.database.reset_mining_tables()

    def print_txs(self):
        """ 
        Function print transactions
        """

        for tx in self.transactions:
            if tx["approved"] and tx["approve_tx"] != 0:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"]+" (Approval TX "+str(tx["approve_tx"])+")")
            else:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"])

        self.write_txs_to_file()

    def get_balance(self, address, actual=True):
        """ 
        Function print transactions
        """
        return self.database.get_balance(address, actual)

    def write_txs_to_file(self):
        """ 
        Function to write transactions to file
        """

        jsonString = json.dumps(self.transactions)
        jsonFile = open("txs/"+str(self.port)+"_txs.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()

    def perform_check_transfers(self, block):
        """ 
        Function to perform checks for transfers

        :param block: block to perform its transfers

        :return: if successful
        """

        #for each transfer
        return self.database.check_transfers(block.hashed_content.transactions)

    def perform_check_transfers_past_block(self, block, block_index):
        """ 
        Function to perform checks for transfers in a past block

        :param block: block to perform its transfers
        :param block_index: the index of a block

        :return: if successful
        """
        #get balances at the previous block index
        past_balances = self.chain.get_balances_at_block(block_index-1)

        #for each transfer
        for tx in block.hashed_content.transactions:
            sender = tx.hashed_content.signed_content.from_ac
            receiver = tx.hashed_content.signed_content.to_ac

            if receiver not in past_balances:
                past_balances[receiver] = 0

            #if account based
            if config.DB_MODEL == "account":
                if sender != config.MINING_SENDER:
                    if past_balances[sender] < 1:
                        return False
                    past_balances[sender] -= 1

                past_balances[receiver] += 1

            #if utxo based
            if config.DB_MODEL == "utxo":
                spent_tx = tx.hashed_content.signed_content.spent_tx

                #if spent tx not in unspent txs
                if sender != config.MINING_SENDER:
                    if spent_tx not in past_balances[sender]:
                        return False

                    past_balances[sender].remove(spent_tx)
                    
                past_balances[receiver].append(tx.hash)
        

        return True

    def perform_transfers(self, block):
        """ 
        Function to perform transforms

        :param block: block to perform its transfers
        """

        #for each transfer
        for tx in block.hashed_content.transactions:
            #make transfer
            self.database.transfer(tx)

    def is_synced(self):
        """ 
        Function to check if synced

        :return: if synced
        """

        return self.local_block_count == self.network_block_count

    def add_pending_tx(self, pending_tx):
        """ 
        Function to add a pending transaction

        :param pending_tx: pending transaction to add
        """
        self.transactions.append(pending_tx)

    def set_pk(self, pk):
        """ 
        Function to set a public key

        :param pk: public key to set
        """
        self.public_key = pk

