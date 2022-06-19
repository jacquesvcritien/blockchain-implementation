import time
import json
from helper_utils import get_hash
from blockHashedContent import BlockHashedContent 
from datetime import datetime
import config as config


class Block:
    def __init__(self, prev_hash):
        """
        Class initialiser

        :param prev_hash: previous hash
        """
        self.hashed_content = BlockHashedContent(prev_hash)
        self.hash = ""

    @classmethod
    def load(cls, hashed_content, hash):
        """
        Function to initialise an object (Another initialiser)

        :param hashed_content: hashed content to add
        :param hash: hashed block hash
        """
        
        new_block = cls(hashed_content["prev_hash"])
        new_block.hashed_content = BlockHashedContent.load(hashed_content)
        new_block.hash = hash
        return new_block

    def increase_nonce(self):
        """
        Function to increase nonce
        """
        self.hashed_content.nonce += 1

    def reset_nonce(self):
        """
        Function to decrease nonce
        """
        self.hashed_content.nonce = 0

    def calculate_hash(self):
        """
        Function to calculate hash
        """
        #get content
        content = self.hashed_content.get_hashed_content()
        payload = json.dumps(content)

        #calculate hash
        self.hash = get_hash(payload)

    def verify(self, database, new_block):
        """
        Function to verify block

        :param database: reference to database
        :param new_block: new block to verify

        :return: whether successful
        """

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

    #function to get block proposer
    def get_block_proposer(self):
        """
        Function to get block proposer

        :return: address of block proposer
        """
        #go through each tx
        for tx in self.hashed_content.transactions:
            #if sender is 0
            if tx.hashed_content.signed_content.from_ac == config.MINING_SENDER:
                return tx.hashed_content.signed_content.to_ac
    

