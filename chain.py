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



