import config as config

class Chain:
    def __init__(self):
        self.blocks = []

    #function to add a block
    def add_block(self, block):
        self.blocks.append(block)

    #function to get prev hash
    def get_prev_hash(self):
        #get number of blocks
        blocks_len = len(self.blocks)
        #if no blocks
        if(blocks_len==0):
            return config.INITIAL_HASH
        else:
            return self.blocks[blocks_len-1].hash

    #get hash of block
    def get_block_hash(self, block_number):
        #if block does not exist
        if len(self.blocks) < block_number:
            return -1

        return self.blocks[block_number-1].hash

    #get block with a specific previous hash
    def get_block_with_prev_hash(self, prev_hash):

        index = 0
        #loop through each block
        for block in self.blocks:
            #if block has the passed in previous hash return the block and its index
            if block.hashed_content.prev_hash == prev_hash:
                return block, index

            #increment index
            index += 1

        return None, -1

    #replace block with given index 
    def replace_block(self, index, new_block, database):

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

    
    #function to get balance at block
    def get_balances_at_block(self, block_index):
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

    #function to print chain
    def print_chain(self):
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



