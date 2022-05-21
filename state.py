from datetime import datetime
import config as config
import time
import json
from helper_utils import get_module_fn
from helper_utils import write_to_file

class State:
    def __init__(self, port, chain):
        self.user_initials = ""
        self.transactions = []
        self.chain = chain
        self.local_block_count = 0
        self.network_block_count = 0
        #read username
        self.read_username()
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

    #function to synchronize
    def synchronize(self, protocol, peers):
        get_blocks_count_msg = protocol.get_block_count()
        peers.broadcast_message(get_blocks_count_msg)

        write_to_file("Syncing and asking for block count", self.logFile)

    #function to read a username
    def read_username(self):
        #keep reading input until its valid 
        while len(self.user_initials) != 2:
            self.user_initials = input("Enter your username: ").upper()
            if len(self.user_initials) != 2:
                print("Username must be the initials (2 characters long)")

        print("Logged in as "+self.user_initials)

    #function to read a transaction
    def get_transaction(self, trn):
        return self.transactions[trn-1]

    #function to get the last tx height
    def get_last_tx_height(self):
        
        #if there are no transactions
        if len(self.transactions) == 0:
            return 0

        return self.transactions[len(self.transactions)-1]["number"]

    #function to get the block count
    def get_block_count(self):
        #if there are no blocks
        if len(self.chain.blocks) == 0:
            return 0

        return len(self.chain.blocks)

    #function to get the block by hash
    def get_block(self, hash):
        #loop through each block
        for block in self.chain.blocks:
            #if block matches, return hash
            if(block.hash == hash):
                return block

        return None

    #function to get the block hashes
    def get_block_hashes(self):

        block_hashes = []

        #loop through blocks
        for block in self.chain.blocks:
            #append hash
            block_hashes.append(block.hash)

        return block_hashes

    #function to get latest hash
    def get_latest_hash(self):
        return self.chain.blocks[-1].hash if len(self.chain.blocks) > 0 else "0"

    #function to insert block
    def insert_block(self, block):
        #increment local count
        self.local_block_count += 1
        self.transactions.clear()

        #if local block count is more than network, increase network
        if(self.local_block_count > self.network_block_count):
            self.network_block_count = self.local_block_count

        #add block to chain
        self.chain.add_block(block)

    #print transactions
    def print_txs(self):
        for tx in self.transactions:
            if tx["approved"] and tx["approve_tx"] != 0:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"]+" (Approval TX "+str(tx["approve_tx"])+")")
            else:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"])

        self.write_txs_to_file()

    #calculates the balance of a user
    def get_balance(self, address):
        return self.database.get_balance(address)

    #function to write to file
    def write_txs_to_file(self):
        jsonString = json.dumps(self.transactions)
        jsonFile = open("txs/"+str(self.port)+"_txs.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()

    #function to perform transfers checks
    def perform_check_transfers(self, block):
        #for each transfer
        return self.database.check_transfers(block.hashed_content.transactions)

    #function to perform transfers checks in a past block
    def perform_check_transfers_past_block(self, block, block_index):
        #get balances at the previous block index
        past_balances = self.chain.get_balances_at_block(block_index-1)

        #for each transfer
        for tx in block.hashed_content.transactions:
            sender = tx.hashed_content.signed_content.from_ac
            receiver = tx.hashed_content.signed_content.to_ac

            #if account based
            if config.DB_MODEL == "account":
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

    #function to perform transfers
    def perform_transfers(self, block):
        #for each transfer
        for tx in block.hashed_content.transactions:
            #make transfer
            self.database.transfer(tx)

    #function to check if synced
    def is_synced(self):
        return self.local_block_count == self.network_block_count

    #function to add pending tx
    def add_pending_tx(self, pending_tx):
        self.transactions.append(pending_tx)

