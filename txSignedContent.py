class TxSignedContent:
    def __init__(self, from_ac, to_ac):
        self.from_ac = from_ac
        self.to_ac = to_ac

    #function to get content as a dict
    def get_signed_content(self):
        return {
            "from_ac": self.from_ac,
            "to_ac": self.to_ac
        }

