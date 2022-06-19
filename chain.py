import config as config

class Chain:
    def __init__(self):
        """
        Class initialiser
        """
        self.blocks = []
        self.possible_blocks = {}

    def add_block(self, block):
        """
        Function to add a block

        :param block: block to add
        """
        self.blocks.append(block)

    def get_prev_hash(self):
        """
        Function to get the current prev hash

        :return: the current previous hash
        """
        #get number of blocks
        blocks_len = len(self.blocks)
        #if no blocks
        if(blocks_len==0):
            return config.INITIAL_HASH
        else:
            return self.blocks[blocks_len-1].hash

    def get_block_hash(self, block_number):
        """
        Function to get the hash of block

        :param block_number: the block number of the block whose hash is returned

        :return: The hash of the block with the passed in block number
        """

        #if block does not exist
        if len(self.blocks) < block_number:
            return -1

        return self.blocks[block_number-1].hash

    def get_block_with_prev_hash(self, prev_hash):
        """
        Function to get block with a specific previous hash

        :param prev_hash: the previous hash of the block to get

        :return: The block with the specified previous hash
        """

        index = 0
        #loop through each block
        for block in self.blocks:
            #if block has the passed in previous hash return the block and its index
            if block.hashed_content.prev_hash == prev_hash:
                return block, index

            #increment index
            index += 1

        return None, -1

    def is_hash_last_block(self, hash):
        """
        Function to check if hash is last hash

        :param hash: hash to check

        :return: if passed in hash is the last hash
        """

        if len(self.blocks) == 0:
            return False

        return hash == self.blocks[-1].hash

    def replace_block(self, index, new_block, database):
        """
        Function to replace block with given index 

        :param index: index to replace
        :param new_block: new block to enter
        :param database: reference to the database
        """

        print("Replacing block", index+1)

        #Revert balances from this index forward
        for i in range (index, len(self.blocks)):
            current_block = self.blocks[i]

            #if account model
            if config.DB_MODEL == "account":
                database.revert_txs(current_block.hashed_content.transactions)
            elif config.DB_MODEL == "utxo":
                database.remove_txs(current_block.hashed_content.transactions)
                #get unspent txs
                unspent_balances = self.get_balances_at_block(index-1)
                database.add_unspent_txs(unspent_balances)

        self.blocks[index] = new_block
        self.blocks = self.blocks[0:index+1]

    
    def get_balances_at_block(self, block_index):
        """
        Function to get balance at block

        :param block_index: block index of the block whose balances are obtained

        :return: the balances at the given block index
        """

        #init balance
        balances = {}

        #if account model
        if config.DB_MODEL == "account":
            #for each block until passed index
            for i in range(0, block_index+1):
                #for each tx in block
                for tx in self.blocks[i].hashed_content.transactions:

                    sender = tx.hashed_content.signed_content.from_ac
                    receiver = tx.hashed_content.signed_content.to_ac

                    #if a key for receiver does not exist, add it
                    if receiver not in balances:
                        balances[receiver] = []

                    #if account is sender, decrease balance
                    balances[sender] -= 1
                    #if account is receiver, increase balance
                    balances[receiver] += 1
        #if account model is utxo
        elif config.DB_MODEL == "utxo":
            #for each block until passed index
            for i in range(0, block_index+1) :
                #for each tx in block
                for tx in self.blocks[i].hashed_content.transactions:

                    sender = tx.hashed_content.signed_content.from_ac
                    receiver = tx.hashed_content.signed_content.to_ac

                    #if a key for receiver does not exist, add it
                    if receiver not in balances:
                        balances[receiver] = []
                    #add unspent tx to receiver
                    balances[receiver].append(tx.hash)

                    #if not a mined tx
                    if sender != config.MINING_SENDER:
                        #remove unspent tx
                        balances[sender].remove(tx.hashed_content.signed_content.spent_tx)

        return balances

    def print_chain(self):
        """
        Function to print chain
        """

        print()
        print()

        counter = 0
        for block in self.blocks:
            counter+=1
            print()
            print("Block", counter)
            print("Hash", block.hash)
            print("Prev hash", block.hashed_content.prev_hash)
            print("Nonce", block.hashed_content.nonce)
            print("Timestamp", block.hashed_content.timestamp)
            print()
            print("--------- TRANSACTIONS ---------")
            tx_count = 0
            for tx in block.hashed_content.transactions:
                tx_count+=1
                print()
                if(tx_count != 1):
                    print("--------------------------------------")
                print("Transaction", tx_count)
                print("TX Signature", tx.hashed_content.signature)
                print("TX Sender", tx.hashed_content.signed_content.from_ac)
                print("TX Receiver", tx.hashed_content.signed_content.to_ac)
                print("TX HASH", tx.hash)
                print()
            print("--------- END OF TRANSACTIONS ---------")
            print()
            print("-------------------------------")

        print()
        print()



