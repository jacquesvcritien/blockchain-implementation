class HashedContent:
    def __init__(self, prev_hash):
        self.prev_hash = prev_hash
        self.nonce = 0
        self.timestamp = None
        self.transactions = []

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
    def get_content(self):
        return {
            "prev_hash": self.prev_hash,
            "nonce": self.nonce,
            "timestamp": self.nonce,
            "transactions": self.get_txs_json()
        }

