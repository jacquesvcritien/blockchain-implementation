from txHashedContent import TxHashedContent 
from txSignedContent import AccountTxSignedContent 
from txSignedContent import UtxoTxSignedContent 
from transaction import Transaction
import config as config

class BlockHashedContent:
    def __init__(self, prev_hash):
        """
        Class initialiser

        :param prev_hash: previous hash
        """

        self.nonce = 0
        self.prev_hash = prev_hash
        self.timestamp = None
        self.transactions = []
    
    @classmethod
    def load(cls, block):
        """
        Function to initialise an object (Another initialiser)

        :param block: block to load data from
        """

        new_hashed_content = cls(block["prev_hash"])
        new_hashed_content.nonce = block["nonce"]
        new_hashed_content.prev_hash = block["prev_hash"]
        new_hashed_content.timestamp = block["timestamp"]
        new_hashed_content.transactions = []

        #for each transaction
        for tx in block["transactions"]:
            spent_tx = None if config.DB_MODEL == "account" else tx["hashedContent"]["spent_tx"]
            hashed_content = TxHashedContent.load(tx["hashedContent"]["from_ac"], tx["hashedContent"]["to_ac"], tx["hashedContent"]["signature"], spent_tx)
            new_tx = Transaction.load(hashed_content, tx["hash"])
            new_hashed_content.transactions.append(new_tx)

        return new_hashed_content

    def add_transaction(self, tx):
        """
        Function to add a transaction

        :param tx: transaction to add
        """
        self.transactions.append(tx)

    def add_pending_txs(self, txs):
        """
        Function to add pending transactions

        :param txs: pending transactions to add
        """
        self.transactions += txs

    def reset_txs(self):
        """
        Function to clear txs
        """
        self.transactions.clear()

    def get_txs_json(self):
        """
        Function to get a json representation of the txs in the block

        :return: a json representation of the txs in the block
        """

        txs = []
        #go through each tx and add its json representation to the list
        for tx in self.transactions:
            txs.append(tx.to_json())
        
        return txs

    def get_hashed_content(self):
        """
        Function to get content as a dict

        :return: block content as a dict
        """

        return {
            "nonce": self.nonce,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "transactions": self.get_txs_json()
        }

