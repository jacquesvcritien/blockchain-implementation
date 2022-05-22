
from helper_utils import write_to_file
from transaction import Transaction
from transaction import Transaction
from block import Block
from helper_utils import get_needed_hash_substring
import config as config
import time

#function to mine block
def mine(miner, block, block_num_to_mine):

    #start timer
    start_time = time.time()

    #needed hash substring not in content hash
    while(not block.hash.startswith(get_needed_hash_substring(config.HASHING_CONSECUTIVE_ZEROS))):

        #if state transactions pool > previous block transactions, reset nonce
        if(len(miner.state.transactions) > len(block.hashed_content.transactions) -1):
        # if(len(miner.state.transactions) > len(block.hashed_content.transactions)):
            #reset nonce
            block.reset_nonce()
            #reset txs
            block.hashed_content.reset_txs()
            # #add mining_tx
            block.hashed_content.add_transaction(miner.current_mining_tx)
            #add pending txs
            block.hashed_content.add_pending_txs(miner.state.transactions)
        
        #if not synced or block is found, halt mining
        if not miner.state.is_synced() or miner.state.local_block_count >= block_num_to_mine:
            return False

        #increase nonce 
        block.increase_nonce()

        #set timestamp
        block.hashed_content.timestamp = int(round(time.time() * 1000))
        #calculate hash
        block.calculate_hash()

    write_to_file("Found hash "+block.hash+" for block "+str(len(miner.state.chain.blocks)+1), miner.logFile)
    write_to_file("--- "+str(time.time() - start_time)+" seconds ---", miner.logFile)

    if miner.state.is_synced() and block_num_to_mine > miner.state.local_block_count:
        #clear pending txs
        miner.state.transactions.clear()
        return True

#function to handle incoming old block for pot
def handle_old_block(protocol, new_block, our_block, our_index, payload_received, new_block_prev_hash):

    #if new hash does not match, check if received block is older
    if payload_received["hash"] != our_block.hash:
        #if our block is older, hence the original
        if int(our_block.hashed_content.timestamp) < int(payload_received["hashedContent"]["timestamp"]):
            print("We found an older block on our chain with the same previous hash", new_block_prev_hash)
            #send our block to the chain
            return False, [protocol.send_block("x", our_block)]
        #otherwise we need to verify
        else:
            print("Need to check hash", payload_received["hash"])
            return True, None

    return False, None

    # #if older block needs to be checked
    # if older_block:
    #     #initialise block
    #     block = Block.load(payload_received["hashedContent"], payload_received["hash"])
    #     #verify block
    #     verified = block.verify(self.state.database, new_block)

    #     #if not verified
    #     if not verified:
    #         print("Block not verified", payload_received["hashedContent"], payload_received["hash"])
    #         return

    #     #we need to replace the block with the same previous hash at the index obtained
    #     #first we need to check if the block transfers were possible in that past block
    #     transfers_acceptable = self.state.perform_check_transfers_past_block(block, our_index)        
    #     print("Replacing block with hash", block.hash)
    #     protocol.state.chain.replace_block(our_index, block, self.state.database)

    #     #perform block transfers
    #     protocol.state.perform_transfers(block)

    #     #reset mining tables
    #     protocol.state.database.reset_mining_tables()

