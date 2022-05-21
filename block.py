import time
import json
from helper_utils import get_hash
from blockHashedContent import BlockHashedContent 
from datetime import datetime
import config as config


class Block:
    def __init__(self, prev_hash):
        self.hashed_content = BlockHashedContent(prev_hash)
        self.hash = ""

    @classmethod
    def load(cls, hashed_content, hash):
        new_block = cls(hashed_content["prev_hash"])
        new_block.hashed_content = BlockHashedContent.load(hashed_content)
        new_block.hash = hash
        return new_block

    #function to increase nonce
    def increase_nonce(self):
        self.hashed_content.nonce += 1

    #function to reset nonce
    def reset_nonce(self):
        self.hashed_content.nonce = 0

    #function to calculate hash of block
    def calculate_hash(self):

        #set date
        self.hashed_content.timestamp = int(round(time.time() * 1000))

        #get content
        content = self.hashed_content.get_hashed_content()
        payload = json.dumps(content)

        #calculate hash
        self.hash = get_hash(payload)

    #function to verify block
    # new_block indicates whether it is a new block or an old block being verified. If it is an old block, transfers should not be checked (they are checked later)
    def verify(self, database, new_block):

        #get content
        content = self.hashed_content.get_hashed_content()
        payload = json.dumps(content)

        #calculate hash
        recalculated_hash = get_hash(payload)

        #if hash does not match
        if recalculated_hash != self.hash:
            print("Block cannot be verified - hash does not match")
            return False

        #check transactions
        for tx in self.hashed_content.transactions:
            #first verify hash
            hash_verified = tx.verify()

            #if not verified
            if not hash_verified:
                print("TX Hash failed to be verified")
                return False

            #check transfers if new block
            if(new_block):
                #check balance
                transfer_allowed=database.check_transfer(tx)

                if not transfer_allowed:
                    print("HERE")
                    print("TX Transfer not allowed - sender out of funds")
                    return False

        #if all transactions passed, verify block
        return True

    

