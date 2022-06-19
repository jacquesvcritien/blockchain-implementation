
from txSignedContent import AccountTxSignedContent 
from txSignedContent import UtxoTxSignedContent 
import config as config

class TxHashedContent:
    def __init__(self, from_ac, to_ac, spent_tx=None):
        """
        Class initialiser

        :param from_ac: transaction's sender
        :param to_ac: transaction's receiver
        :param spent_tx: the spent transaction if it is using PoT
        """
        self.signed_content = AccountTxSignedContent(from_ac, to_ac) if spent_tx == None else UtxoTxSignedContent(from_ac, to_ac, spent_tx)
        self.signature = ""

    @classmethod
    def load(cls, from_ac, to_ac, signature, spent_tx=None):
        """
        Function to load a transaction's hashed content

        :param from_ac: transaction's sender
        :param to_ac: transaction's receiver
        :param signature: the transaction's signature
        :param spent_tx: the spent transaction if it is using PoT
        """
        new_tx_hashed_content = cls(from_ac, to_ac, spent_tx)
        new_tx_hashed_content.signature = signature

        return new_tx_hashed_content

    def get_hashed_content(self):
        """
        Function to get content as a dictionary

        :return: content as a dictionary
        """
        tx = {
            "from_ac": self.signed_content.from_ac,
            "to_ac": self.signed_content.to_ac,
            "signature": self.signature
        }

        #if utxo, add spent tx
        if config.DB_MODEL == "utxo":
            tx["spent_tx"] = self.signed_content.spent_tx

        return tx

