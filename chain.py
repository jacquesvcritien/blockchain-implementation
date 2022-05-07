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
            return "0"
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
    def replace_block(self, index, block):
        self.blocks[index] = block

        #TODO: Revert old balances of bad block

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
                print("TX Content", tx.hashed_content.signed_content.to_ac)
                print("TX HASH", tx.hash)
                print()
            print("--------- END OF TRANSACTIONS ---------")
            print()
            print("-------------------------------")

        print()
        print()



