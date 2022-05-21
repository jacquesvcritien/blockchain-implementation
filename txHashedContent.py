
from txSignedContent import AccountTxSignedContent 
from txSignedContent import UtxoTxSignedContent 
import config as config

class TxHashedContent:
    def __init__(self, from_ac, to_ac, spent_tx=None):
        self.signed_content = AccountTxSignedContent(from_ac, to_ac) if spent_tx == None else UtxoTxSignedContent(from_ac, to_ac, spent_tx)
        self.signature = ""

    @classmethod
    def load(cls, from_ac, to_ac, signature, spent_tx=None):
        new_tx_hashed_content = cls(from_ac, to_ac, spent_tx)
        new_tx_hashed_content.signature = signature

        return new_tx_hashed_content

    #function to get content as a dict
    def get_hashed_content(self):
        tx = {
            "from_ac": self.signed_content.from_ac,
            "to_ac": self.signed_content.to_ac,
            "signature": self.signature
        }

        #if utxo, add spent tx
        if config.DB_MODEL == "utxo":
            tx["spent_tx"] = self.signed_content.spent_tx

        return tx

