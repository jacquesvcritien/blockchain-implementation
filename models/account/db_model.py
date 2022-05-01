
import sqlite3

class Database:
    def __init__(self):
        self.database = sqlite3.connect('blockchain.db', check_same_thread=False)
        self.cursor = self.database.cursor()

        #create tables if they do not exist
        self.cursor.execute("create table if not exists actual_balances (account varchar(42) primary key, balance int)")
        self.cursor.execute("create table if not exists mining_balances (account varchar(42) primary key, balance int)")

    #function to get balance of account
    def get_balance(self, account, actual=True):
        #get balance
        table_name = "actual_balances" if actual else "mining_balances"
        balance = self.cursor.execute("SELECT balance from "+table_name+" where account='"+account+"'").fetchall()

        return 0 if (len(balance) == 0) else balance[0][0]

    # function to check if record for account exists
    def account_row_exists(self, account, actual=True):
        table_name = "actual_balances" if actual else "mining_balances"
        return len(self.cursor.execute("select 1 from "+table_name+" where account='"+account+"' limit 1").fetchall()) == 1

    #function to increase balance of account
    def __increase_balance(self, account, actual=True):
        table_name = "actual_balances" if actual else "mining_balances"

        #if account exist, increment balance
        if(self.account_row_exists(account, actual)):
            self.cursor.execute("UPDATE "+table_name+" SET balance = balance + 1 where account='"+account+"'")
        #otherwise, set balance to 1
        else:
            self.cursor.execute("insert into  "+table_name+" (account, balance) values ('"+account+"', 1)")
        self.database.commit()

    #function to decrease balance of account
    def __decrease_balance(self, account, actual=True):
        table_name = "actual_balances" if actual else "mining_balances"
        #if exists
        if(self.account_row_exists(account, actual)):
            #get current balance
            current_balance = self.get_balance(account, actual)
            #if has balance more than 0, decrease balance
            if current_balance > 0:
                self.cursor.execute("UPDATE "+table_name+" SET balance = balance - 1 where account='"+account+"'")
                return 
            
        raise Exception("Not enough balance to decrease")


    #function to execute a transfer if possible
    def transfer(self, from_ac, to, actual=True):
        #check if the sender has enough balance
        if self.get_balance(from_ac, actual) < 1 and from_ac != "0":
            return False

        #increase balance of receiver
        self.__increase_balance(to, actual)

        #decrease balance of sender
        if(from_ac != "0"):
            self.__decrease_balance(from_ac, actual)

    #function to check if a transfer is possible
    def check_transfer(self, from_ac, to, actual=True):
        #check if the sender has enough balance
        if self.get_balance(from_ac, actual) < 1 and sender != "0":
            return False

        return True

    #function to print balances
    def print_balances(self, actual=True):
        table_name = "actual_balances" if actual else "mining_balances"
        balances = self.cursor.execute("select * from "+table_name).fetchall()
        for balance in balances:
            print(balance[0]+": "+str(balance[1]))

    #function to reset mining balances
    def reset_mining_balances(self):
        self.cursor.execute("delete from mining_balances")
        self.cursor.execute("insert into mining_balances select * from actual_balances")




