
from txSignedContent import TxSignedContent 

class TxHashedContent:
    def __init__(self, from_ac, to_ac):
        self.signed_content = TxSignedContent(from_ac, to_ac)
        self.signature = ""

    @classmethod
    def load(cls, from_ac, to_ac, signature):
        new_tx_hashed_content = cls(from_ac, to_ac)
        new_tx_hashed_content.signature = signature

        return new_tx_hashed_content

    #function to get content as a dict
    def get_hashed_content(self):
        return {
            "from_ac": self.signed_content.from_ac,
            "to_ac": self.signed_content.to_ac,
            "signature": self.signature
        }

