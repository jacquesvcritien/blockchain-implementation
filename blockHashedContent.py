from txHashedContent import TxHashedContent 
from txSignedContent import TxSignedContent 
from transaction import Transaction

class BlockHashedContent:
    def __init__(self, prev_hash):
        self.nonce = 0
        self.prev_hash = prev_hash
        self.timestamp = None
        self.transactions = []
    
    @classmethod
    def load(cls, block):
        new_hashed_content = cls(block.prev_hash)
        new_hashed_content.nonce = block.nonce
        new_hashed_content.prev_hash = block.prev_hash
        new_hashed_content.timestamp = block.timestamp
        new_hashed_content.transactions = []

        #for each transaction
        for tx in block.transactions:
            signed_content = TxSignedContent(tx.hashedContent.from_ac, tx.hashedContent.from_ac)
            hashed_content = TxHashedContent(signed_content, tx.hashedContent.signature)
            new_tx = Transaction(hashed_content, hashed_content)
            new_hashed_content.transactions.append(new_tx)

        return new_hashed_content

    #function to add a transaction
    def add_transaction(self, tx):
        self.transactions.append(tx)

    #returns a json representation of the txs in the block
    def get_txs_json(self):
        txs = []
        #go through each tx and add its json representation to the list
        for tx in self.transactions:
            txs.append(tx.to_json())
        
        return txs

    #function to get content as a dict
    def get_hashed_content(self):
        return {
            "nonce": self.nonce,
            "prev_hash": self.prev_hash,
            "timestamp": self.nonce,
            "transactions": self.get_txs_json()
        }

