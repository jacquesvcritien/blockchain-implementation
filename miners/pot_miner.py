
from helper_utils import write_to_file
from transaction import Transaction
from block import Block
from helper_utils import get_needed_hash_substring
import config as config
import time
import hashlib
import random

#function to mine block
def mine(miner, block, block_num_to_mine):

    #start timer
    start_time = time.time()

    prev_hash =  block.hashed_content.prev_hash

    #get next proposer
    next_proposer = get_peer_with_least_value(miner.peers, block.hashed_content.prev_hash)

    #if multiple possible proposers
    if len(next_proposer) > 1:
        #add to block deadlocks to check
        miner.block_deadlocks[prev_hash] = next_proposer

    #check if to mine
    to_propose = check_if_proposer(miner.wallet.public_key, next_proposer)

    if to_propose:
        print("Proposing", block_num_to_mine)

        #wait for block time
        milliseconds_now = int(round(time.time() * 1000))
        #get next block time by adding block time to the timestamp of the previous block

        next_block_time = (int(config.BLOCK_TIME) + int(miner.chain.blocks[-1].hashed_content.timestamp)) if block_num_to_mine > 1 else (int(config.BLOCK_TIME) + milliseconds_now)
        # while(milliseconds_now < next_block_time):
        #     milliseconds_now = int(round(time.time() * 1000))
        time_to_sleep = ((next_block_time-milliseconds_now)/1000)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        #set random nonce
        block.hashed_content.nonce = random.randint(0,9999999)
        #add pending txs
        block.hashed_content.add_pending_txs(miner.state.transactions)
        #add timestmap
        block.hashed_content.timestamp = next_block_time

        #if state transactions pool > current block txs, add pending txs
        # -1 is the current_mining_tx
        if(len(miner.state.transactions) > len(block.hashed_content.transactions) -1):
        # if(len(miner.state.transactions) > len(block.hashed_content.transactions)):
            #reset txs
            block.hashed_content.reset_txs()
            # #add mining_tx
            block.hashed_content.add_transaction(miner.current_mining_tx)
            #add pending txs
            block.hashed_content.add_pending_txs(miner.state.transactions)

        #calculate hash
        block.calculate_hash()

        write_to_file("Found hash "+block.hash+" for block "+str(len(miner.chain.blocks)+1), miner.logFile)
        write_to_file("--- "+str(time.time() - start_time)+" seconds ---", miner.logFile)

        # if miner.state.is_synced() and block_num_to_mine > miner.state.local_block_count:
        #     #clear pending txs
        #     miner.state.transactions.clear()
        #     return True
        # else:
        #     return False
        return True
    else:
        time.sleep(int(config.BLOCK_TIME)/2000)

def calculate_value_for_pk(public_key, prev_hash):
    #concat public key with previp=ous hash
    to_hash = public_key+prev_hash
    #hash concetination
    hashed = hashlib.sha256(to_hash.encode(config.BYTE_ENCODING_TYPE)).hexdigest()
    #get ls64b
    ls64b = hashed[-8:]
    val = int(hashed[-8:], 16)
    return val

def get_peer_with_least_value(peers, prev_hash):
    result = []

    least_val = 9999999999999999

    for peer in peers.peers:
        if "public_key" in peer:
            val = calculate_value_for_pk(peer["public_key"], prev_hash)

            if val < least_val:
                least_val = val
                result = [peer]

    return result

#function to check if miner should mine
def check_if_proposer(public_key, next_proposers):
    for next_proposer in next_proposers:
        if public_key == next_proposer["public_key"]:
            return True

    return False

#function to handle incoming old block for pot
#returns flag whether to verify and if verify replace
def handle_old_block(protocol, new_block, our_block, our_index, payload_received, new_block_prev_hash):

    #get new block proposer
    block_proposer = new_block.get_block_proposer()
    #calculate pot value for new block
    new_block_pot_value = calculate_value_for_pk(block_proposer, new_block_prev_hash)

    #if new hash does not match, check if received block is older
    if payload_received["hash"] != our_block.hash:
        #if a block with the same previous hash is found
        if our_block != None:
            #calculate pot value for our block
            #get block proposer
            our_block_proposer = our_block.get_block_proposer()
            #calculate pot value
            our_block_pot_value = calculate_value_for_pk(our_block_proposer, our_block.hashed_content.prev_hash)

            #if new block pot value is less than our block's pot value, replace
            if(new_block_pot_value < our_block_pot_value):
                print("Value lower than our block")
                return True, None
            #if new block pot value is larger than our block's pot value, send our block
            elif(new_block_pot_value > our_block_pot_value):
                print("Value higher than our block")
                # return False, [protocol.send_block("x", our_block)]
                return False, None
            #if they are equal - two propers
            elif(new_block_pot_value == our_block_pot_value):
                #check if possible block is found in chain's possible blocks
                found_possible_block = new_block.hash in protocol.state.chain.possible_blocks
                #get next block previous hash
                next_block_prev_hash = new_block.hash
                #this is a counter to check our chain's blocks
                counter = 1
                #check next blocks until not equal or not found
                while(found_possible_block):
                    #get value of next block
                    next_block_pot_value = protocol.state.chain.possible_blocks[next_block_prev_hash]["pot_value"]
                    next_block_hash = protocol.state.chain.possible_blocks[next_block_prev_hash]["hash"]

                    #get our next block's pot value
                    our_next_block = protocol.state.chain.blocks[our_index+counter]
                    our_next_block_proposer = our_block.get_block_proposer()
                    our_next_block_pot_value = calculate_value_for_pk(our_next_block_proposer, our_next_block.hashed_content.prev_hash)
                    #check with our block
                    #if new block pot value is less than our block's pot value, replace
                    if(next_block_pot_value < our_next_block_pot_value):
                        return True, None
                    #if new block pot value is larger than our block's pot value, send our block
                    elif(next_block_pot_value > our_next_block_pot_value):
                        #send all our blocks from the given block onwards
                        blocks_to_send = []
                        for i in range(our_index, len(protocol.state.chain.blocks)):
                            blocks_to_send.append(protocol.send_block("x", protocol.state.chain.blocks[i]))
                        # return False, blocks_to_send
                        return False, None

                    #check if possible block is found in chain's possible blocks
                    found_possible_block = next_block_hash in protocol.state.chain.possible_blocks

                #if no possible blocks were found
                return False, None
        #if no block with the same previous hash is found
        else:
            #store pot value
            protocol.state.chain.possible_blocks[new_block_prev_hash] = {
                "pot_value": value,
                "hash": new_block.hash
            }

    return False, None