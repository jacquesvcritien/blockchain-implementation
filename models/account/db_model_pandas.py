
import pandas as pd

class Database:
    def __init__(self):
        self.database = pd.DataFrame(columns=['Account', 'Balance'])
        self.mining_database = pd.DataFrame(columns=['Account', 'Balance'])

    #function to get balance of account
    def get_balance(self, account):
        #check if account exists
        if(self.account_row_exists(account)):
            return self.database.loc[self.database['Account'] == account]["Balance"].values[0]
        else:
            return 0

    #function to check if record for account exists
    def account_row_exists(self, account):
        return account in self.database['Account'].values

    #function to increase balance of account
    def __increase_balance(self, account):
        #if account exists
        if(self.account_row_exists(account)):
            #increment balance
            self.database.loc[self.database['Account'] == account, "Balance"] += 1
        else:
            #create account with 1
            self.database = self.database.append({'Account': account, 'Balance': 1}, ignore_index=True)

    #function to decrease balance of account
    def __decrease_balance(self, account):
        #if exists
        if(self.account_row_exists(account)):
            #get current balance
            current_balance = self.database.loc[self.database['Account'] == account]["Balance"].values[0]
            #if has balance more than 1, decrease balance
            if current_balance > 1:
                self.database.loc[self.database['Account'] == account, "Balance"]-= 1
            #if balance is 1, remove row
            else:
                self.database.drop(self.database.index[self.database['Account'] == account], inplace=True)

    #function to execute a transfer if possible
    def transfer(self, from_ac, to):
        #check if the sender has enough balance
        if self.get_balance(from_ac) < 1 and from_ac != "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000":
            return False

        #increase balance of receiver
        self.__increase_balance(to)
        #decrease balance of sender
        self.__decrease_balance(from_ac)

    #function to check if a transfer is possible
    def check_transfer(self, from_ac, to):
        #check if the sender has enough balance
        if self.get_balance(from_ac) < 1 and sender != "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000":
            return False

        return True
        




