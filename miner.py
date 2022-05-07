from transaction import Transaction
from block import Block
from helper_utils import get_needed_hash_substring
import time
import config as config
from helper_utils import write_to_file

class Miner:
    def __init__(self, wallet, chain, state, protocol, peers):
        self.wallet = wallet
        self.chain = chain
        self.state = state
        self.protocol = protocol
        self.peers = peers
        self.logFile = open('logs/mine_log_'+str(state.port)+'.txt', 'w')

    #function to mine block
    def mine(self, block, block_num_to_mine):

        #start timer
        start_time = time.time()

        #reset mining balances
        self.state.database.reset_mining_balances()

        #if state transactions pool > previous block transactions, reset nonce
        if(len(self.state.transactions) > len(block.hashed_content.transactions)):
            print("Resetting nonce")
            block.reset_nonce()

        #needed hash substring not in content hash
        while(not block.hash.startswith(get_needed_hash_substring(config.HASHING_CONSECUTIVE_ZEROS))):
            
            #if not synced or block is found, halt mining
            if not self.state.is_synced() or self.state.local_block_count >= block_num_to_mine:
                print("Node not synced")
                return False

            #increase nonce 
            block.increase_nonce()
            #calculate hash
            block.calculate_hash()

        #empty state transaction pool
        self.state.transactions = []

        write_to_file("Found hash "+block.hash+" for block "+str(len(self.chain.blocks)+1), self.logFile)
        write_to_file("--- "+str(time.time() - start_time)+" seconds ---", self.logFile)

        return self.state.is_synced() and block_num_to_mine > self.state.local_block_count


    #function to mine
    def run(self):
        while(True):
            #if synced
            if self.state.is_synced():
                #get previous hash
                prev_hash = self.chain.get_prev_hash()

                #initialise a block
                block = Block(prev_hash)

                #generate a transaction for the receipt of the mining conpensation
                new_tx = self.add_transaction()
                block.hashed_content.add_transaction(new_tx)

                #get block number to mine
                block_num_to_mine = len(self.chain.blocks)+1
                #mine
                mined = self.mine(block, block_num_to_mine)

                #if successfully mined
                if mined:
                    #perform transfers
                    self.state.perform_transfers(block)

                    #add block
                    self.state.insert_block(block)

                    #send new block to neighbours
                    new_block_msg = self.protocol.new_block(block)
                    self.peers.broadcast_message_bytes(new_block_msg)
                else:
                    self.state.synchronize(self.protocol, self.peers)
            else:
                self.state.synchronize(self.protocol, self.peers)

    #function to add a transaction
    def add_transaction(self):
        #create a tx to the user himself/herself
        tx = Transaction("0", self.wallet.public_key)
        tx.calculate_hash_sign(self.wallet)
        return tx