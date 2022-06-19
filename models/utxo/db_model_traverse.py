
import config as config
import copy
from block import Block

class Database:
    def __init__(self, chain, pending_txs):
        """
        Class initialiser

        :param chain: chain to set
        :param pending_txs: pending transactions
        """

        self.chain = chain
        self.pending_txs = pending_txs

    def get_balance(self, account, actual=True):
        """
        Function to get balance of account

        :param account: account to get its balance
        :param actual: if to use the actual or mining table
        
        :return: the balance of the given account
        """

        chain_type = "actual" if actual else "mining"
        unspent_txs = []
        for block in self.chain.blocks:
            #if block is confirmed
            if block.hashed_content.timestamp != None:
                for tx in block.hashed_content.transactions:
                    #get hash, receiver and spent tx
                    hash = tx.hash
                    receiver = tx.hashed_content.signed_content.to_ac
                    sender = tx.hashed_content.signed_content.from_ac
                    spent_tx = tx.hashed_content.signed_content.spent_tx

                    #if receiver, add tx to spent tx
                    if receiver == account:
                        unspent_txs.append(hash)

                    #if spent tx is in unspent txs, remove it
                    if spent_tx in unspent_txs and sender == account:
                        unspent_txs.remove(spent_tx)

        if not actual:
            for tx in self.pending_txs:
                #get hash, receiver and spent tx
                hash = tx.hash
                receiver = tx.hashed_content.signed_content.to_ac
                sender = tx.hashed_content.signed_content.from_ac
                spent_tx = tx.hashed_content.signed_content.spent_tx

                #if receiver, add tx to spent tx
                if receiver == account:
                    unspent_txs.append(hash)

                #if spent tx is in unspent txs, remove it
                if spent_tx in unspent_txs and sender == account:
                    unspent_txs.remove(spent_tx)

        return len(unspent_txs)

    def get_unspent_txs(self, account, actual=True):
        """
        Function to get unspent txs of account

        :param account: account to get its unspent txs
        :param actual: if to use the actual or mining table
        
        :return: unspent txs of account
        """

        chain_type = "actual" if actual else "mining"
        unspent_txs = []
        for block in self.chain.blocks:
            #if block is confirmed
            if block.hashed_content.timestamp != None:
                for tx in block.hashed_content.transactions:
                    #get hash, receiver and spent tx
                    hash = tx.hash
                    receiver = tx.hashed_content.signed_content.to_ac
                    sender = tx.hashed_content.signed_content.from_ac
                    spent_tx = tx.hashed_content.signed_content.spent_tx

                    #if receiver, add tx to spent tx
                    if receiver == account:
                        unspent_txs.append(hash)

                    #if spent tx is in unspent txs, remove it
                    if spent_tx in unspent_txs and sender == account:
                        unspent_txs.remove(spent_tx)

        if not actual:
            for tx in self.pending_txs:
                #get hash, receiver and spent tx
                hash = tx.hash
                receiver = tx.hashed_content.signed_content.to_ac
                sender = tx.hashed_content.signed_content.from_ac
                spent_tx = tx.hashed_content.signed_content.spent_tx

                #if receiver, add tx to spent tx
                if receiver == account:
                    unspent_txs.append(hash)

                #if spent tx is in unspent txs, remove it
                if spent_tx in unspent_txs and sender == account:
                    unspent_txs.remove(spent_tx)

        return unspent_txs

    #function to get balance of account
    def get_balances(self, actual=True):
        """
        Function to get balances of accounts

        :param actual: if to use the actual or mining table
        
        :return: all the balances of the either the actual or mining table
        """

        chain_type = "actual" if actual else "mining"
        balances = {}
        for block in self.chain.blocks:
            #if block is confirmed
            if block.hashed_content.timestamp != None:
                for tx in block.hashed_content.transactions:
                    #get hash, receiver and spent tx
                    hash = tx.hash
                    receiver = tx.hashed_content.signed_content.to_ac
                    sender = tx.hashed_content.signed_content.from_ac
                    spent_tx = tx.hashed_content.signed_content.spent_tx

                    if receiver not in balances:
                        balances[receiver] = []

                    #if receiver, add tx to spent tx
                    balances[receiver].append(hash)

                    #if spent tx is in unspent txs, remove it
                    if sender != config.MINING_SENDER:
                        balances[sender].remove(spent_tx)

        if not actual:
            for tx in self.pending_txs:
                #get hash, receiver and spent tx
                hash = tx.hash
                receiver = tx.hashed_content.signed_content.to_ac
                sender = tx.hashed_content.signed_content.from_ac
                spent_tx = tx.hashed_content.signed_content.spent_tx

                if receiver not in balances:
                    balances[receiver] = []

                #if receiver, add tx to spent tx
                balances[receiver].append(hash)

                #if spent tx is in unspent txs, remove it
                if sender != config.MINING_SENDER:
                    balances[sender].remove(spent_tx)

        return balances

    #function to execute a transfer if possible
    def transfer(self,tx, actual=True):
        
        #get from
        from_ac = tx.hashed_content.signed_content.from_ac

        #get user unspent txs
        unspent_txs = self.get_unspent_txs(from_ac, actual)
        
        #check if the sender has an unspent tx
        if tx.hashed_content.signed_content.spent_tx not in unspent_txs and from_ac != config.MINING_SENDER:
            return False

    def check_transfer(self, tx, actual=True):
        """
        Function to check if a transfer is possible

        :param tx: tx to check
        :param actual: if to use the actual or mining table

        :return: whether possible
        """

        chain_type = "actual" if actual else "mining"

        #get from 
        from_ac = tx.hashed_content.signed_content.from_ac
        #get to
        to_ac = tx.hashed_content.signed_content.to_ac
        #get spent tx
        spent_tx = tx.hashed_content.signed_content.spent_tx

        #check if the sender has an unspent tx with that number
        mined_tx = from_ac == config.MINING_SENDER

        #get user unspent txs
        unspent_txs = self.get_unspent_txs(from_ac, actual)

        if(spent_tx not in unspent_txs and not mined_tx):
            return False
        
        return True

    def check_transfers(self, txs, actual=True):
        """
        Function to check if set of transfers are possible

        :param txs: txs to check
        :param actual: if to use the actual or mining table

        :return: whether possible
        """
        
        balances = self.get_balances(actual)
        #for each tx
        for tx in txs:
            #get from 
            from_ac = tx.hashed_content.signed_content.from_ac
            #get to
            to_ac = tx.hashed_content.signed_content.to_ac
            #get spent_tx
            spent_tx = tx.hashed_content.signed_content.spent_tx

            #check if the sender has enough balance
            if from_ac != config.MINING_SENDER:
                if from_ac not in balances:
                    return False
                if spent_tx not in balances[from_ac]:
                    return False

                balances[from_ac].remove(spent_tx)

            #check if exists
            if to_ac not in balances:
                balances[to_ac] = []

            balances[to_ac].append(tx.hash)

        return True

    def print_balances(self, actual=True):
        """
        Function to print balances

        :param actual: if to use the actual or mining table
        """

        balances = self.get_balances(actual)
        for balance in balances:
            print(balance+": "+str(len(balances[balance])))

    def print_unspent_txs(self, account, actual=True):
        """
        Function to print unspent transactions

        :param account: account to get its unspent txs
        :param actual: if to use the actual or mining table
        """
        unspent_txs = self.get_unspent_txs(account, actual)
        for unspent_tx in unspent_txs:
            print(unspent_tx)


    def reset_mining_tables(self):
        """
        This is not used in this case
        """
        return

    def remove_txs(self, txs):
        """
        This is not used in this case
        """
        return 

    def add_unspent_txs(self, unspent_balances):
        """
        This is not used in this case
        """
        return