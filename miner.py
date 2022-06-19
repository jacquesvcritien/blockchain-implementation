from transaction import Transaction
from block import Block
from helper_utils import get_needed_hash_substring
import time
import config as config
from helper_utils import get_module_fn
from helper_utils import write_to_file

class Miner:
    def __init__(self, wallet, chain, state, protocol, peers):
        """
        Class initialiser

        :param wallet: a reference to the initialised wallet
        :param chain: a reference to the initialised chain
        :param state: a reference to the initialised state
        :param protocol: the protocol to be used
        :param peers: the miner's peers
        """
        
        self.wallet = wallet
        self.chain = chain
        self.state = state
        self.protocol = protocol
        self.peers = peers
        self.logFile = open('logs/mine_log_'+str(state.port)+'.txt', 'w')

    def run(self):
        """
        The miner's main runner function
        """
        
        while(True):
            #if synced
            if self.state.is_synced():
                #get previous hash
                prev_hash = self.chain.get_prev_hash()

                #initialise a block
                block = Block(prev_hash)

                #generate a transaction for the receipt of the mining conpensation
                self.current_mining_tx = self.add_transaction()
                #add mining_tx
                # self.state.transactions.append(self.current_mining_tx)
                block.hashed_content.add_transaction(self.current_mining_tx)

                #get block number to mine
                block_num_to_mine = len(self.chain.blocks)+1
                #mine
                mine = get_module_fn("miners."+config.MINING_TYPE+"_miner", "mine")
                mined = mine(self, block, block_num_to_mine)

                #if successfully mined
                if mined:
                    #if previous hash matches previous block's hash
                    if(block_num_to_mine == 1 or block.hashed_content.prev_hash == self.chain.blocks[block_num_to_mine-2].hash):
                        #add block
                        self.state.insert_block(block)

                        print("Found block", block_num_to_mine)

                        #send new block to neighbours
                        new_block_msg = self.protocol.new_block(block)
                        self.peers.broadcast_message(new_block_msg)
            else:
                self.state.synchronize(self.protocol, self.peers)

    def add_transaction(self):
        """
        Function to add the first miner transaction to a block 
        """

        #create a tx to the user himself/herself
        spent_tx = None if config.DB_MODEL == "account" else config.INITIAL_HASH
        tx = Transaction(config.MINING_SENDER, self.wallet.public_key, spent_tx)
        tx.calculate_hash_sign(self.wallet)
        return tx