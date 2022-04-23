from transaction import Transaction
from block import Block

class Miner:
    def __init__(self, wallet, chain):
        self.wallet = wallet
        self.chain = chain
        self.run()

    #function to mine
    def run(self):
        while(True):
            #get previous hash
            prev_hash = self.chain.get_prev_hash()

            #initialise a block
            block = Block(prev_hash)

            #generate a transaction for the receipt of the mining conpensation
            new_tx = self.add_transaction()
            block.hashed_content.add_transaction(new_tx)

            block.calculate_hash()

            self.chain.add_block(block)
            self.chain.print_chain()


    #function to add a transaction
    def add_transaction(self):
        #create a tx to the user himself/herself
        tx = Transaction("00", self.wallet.user_initials)
        tx.calculate_hash_sign(self.wallet)
        return tx