
import config as config
import copy
from block import Block

class Database:
    def __init__(self, chain, pending_txs):
        self.chains = {
            "actual": chain,
            "mining": copy.deepcopy(chain)
        }
        self.chain = chain
        self.pending_txs = pending_txs

    #function to get balance of account
    def get_balance(self, account, actual=True):
        chain_type = "actual" if actual else "mining"
        unspent_txs = []
        # for block in self.chains[chain_type].blocks:
        for block in self.chain.blocks:
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

    #function to get unspent txs of account
    def get_unspent_txs(self, account, actual=True):
        chain_type = "actual" if actual else "mining"
        unspent_txs = []
        # for block in self.chains[chain_type].blocks:
        for block in self.chain.blocks:
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
        chain_type = "actual" if actual else "mining"
        balances = {}
        # for block in self.chains[chain_type].blocks:
        for block in self.chain.blocks:
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

        # #add tx to last block
        # if len(self.chains[chain_type].blocks) == 0:
        #     block = Block(config.INITIAL_HASH)
        #     self.chains[chain_type].blocks.append(block)

        # self.chains[chain_type].blocks[-1].hashed_content.transactions.append(tx)

    #function to check if a transfer is possible
    def check_transfer(self, tx, actual=True):

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

    #function to check if set of transfers are possible
    def check_transfers(self, txs, actual=True):

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

    #function to print balances
    def print_balances(self, actual=True):
        balances = self.get_balances(actual)
        for balance in balances:
            print(balance+": "+str(len(balances[balance])))

    #function to print unspent txs
    def print_unspent_txs(self, account, actual=True):
        unspent_txs = self.get_unspent_txs(account, actual)
        for unspent_tx in unspent_txs:
            print(unspent_tx)


    #function to reset mining balances
    def reset_mining_tables(self):
        # self.chains["mining"] = copy.deepcopy(self.chains["actual"])
        return

    #function to remove txs for replacing block
    def remove_txs(self, txs):
        self.reset_mining_tables()

    #function to add unspect txs for replacing block
    def add_unspent_txs(self, unspent_balances):
        self.reset_mining_tables()