class AccountTxSignedContent:
    def __init__(self, from_ac, to_ac):
        self.from_ac = from_ac
        self.to_ac = to_ac

    #function to get content as a dict
    def get_signed_content(self):
        return {
            "from_ac": self.from_ac,
            "to_ac": self.to_ac
        }

class UtxoTxSignedContent:
    def __init__(self, from_ac, to_ac, spent_tx):
        self.from_ac = from_ac
        self.to_ac = to_ac
        self.spent_tx = spent_tx

    #function to get content as a dict
    def get_signed_content(self):
        return {
            "from_ac": self.from_ac,
            "to_ac": self.to_ac,
            "spent_tx": self.spent_tx
        }

