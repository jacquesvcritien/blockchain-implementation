from transaction import Transaction
from block import Block
from helper_utils import get_needed_hash_substring
import time
import config as config
from helper_utils import write_to_file

class Miner:
    def __init__(self, wallet, chain, state):
        self.wallet = wallet
        self.chain = chain
        self.state = state
        self.logFile = open('logs/mine_log_'+str(state.port)+'.txt', 'w')

    #function to mine block
    def mine(self, block):

        #start timer
        start_time = time.time()

        #reset mining balances
        self.state.database.reset_mining_balances()

        #if state transactions pool > previous block transactions, reset nonce
        if(len(self.state.transactions) > len(block.hashed_content.transactions)):
            block.reset_nonce()

        #needed hash substring not in content hash
        while(not block.hash.startswith(get_needed_hash_substring(config.HASHING_CONSECUTIVE_ZEROS))):
            #increase nonce 
            block.increase_nonce()
            #calculate hash
            block.calculate_hash()

        #empty state transaction pool
        self.state.transactions = []

        write_to_file("Found hash "+block.hash+" for block "+str(len(self.chain.blocks)+1), self.logFile)
        write_to_file("--- "+str(time.time() - start_time)+" seconds ---", self.logFile)

        # print("Found hash", block.hash)
        # print("--- %s seconds ---" % (time.time() - start_time))


    #function to mine
    def run(self):
        while(True):
            #get previous hash
            prev_hash = self.chain.get_prev_hash()

            #initialise a block
            block = Block(prev_hash)

            #generate a transaction for the receipt of the mining conpensation
            new_tx = self.add_transaction()
            block.hashed_content.add_transaction(new_tx)

            #mine
            self.mine(block)
            #perform transfers
            self.state.perform_transfers(block)

            #add block
            self.chain.add_block(block)

    #function to add a transaction
    def add_transaction(self):
        #create a tx to the user himself/herself
        tx = Transaction("0", self.wallet.public_key)
        tx.calculate_hash_sign(self.wallet)
        return tx