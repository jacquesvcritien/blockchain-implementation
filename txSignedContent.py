class AccountTxSignedContent:
    def __init__(self, from_ac, to_ac):
        """
        Class initialiser

        :param from_ac: transaction's sender
        :param to_ac: transaction's receiver
        """
        self.from_ac = from_ac
        self.to_ac = to_ac

    def get_signed_content(self):
        """
        Function to get content as a dict

        :return: The signed content as a dict
        """
        return {
            "from_ac": self.from_ac,
            "to_ac": self.to_ac
        }

class UtxoTxSignedContent:
    def __init__(self, from_ac, to_ac, spent_tx):
        """
        Class initialiser

        :param from_ac: transaction's sender
        :param spent_tx: the spent transaction
        """
        self.from_ac = from_ac
        self.to_ac = to_ac
        self.spent_tx = spent_tx

    #function to get content as a dict
    def get_signed_content(self):
        """
        Function to get content as a dict

        :return: The signed content as a dict
        """
        return {
            "from_ac": self.from_ac,
            "to_ac": self.to_ac,
            "spent_tx": self.spent_tx
        }

