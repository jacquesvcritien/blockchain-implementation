
import sqlite3
import config as config
import threading

class Database:
    def __init__(self, port):
        """
        Class initialiser

        :param port: the port used to name the database file
        """

        #create db
        self.database = sqlite3.connect('dbs/'+str(port)+'_db_account.db', check_same_thread=False)
        self.cursor = self.database.cursor()
        self.lock = threading.Lock()

        #create tables if they do not exist
        self.db_safe_execute("create table if not exists actual_balances (account varchar(42) primary key, balance int)")
        self.db_safe_execute("create table if not exists mining_balances (account varchar(42) primary key, balance int)")

    def db_safe_execute(self, command):
        """
        Function to execute commands with lock

        :param command: command to execute

        :return: the result from the execution
        """
        try:
            self.lock.acquire(True)
            return self.cursor.execute(command)
        finally:
            self.lock.release()

    def get_balance(self, account, actual=True):
        """
        Function to get balance of account

        :param account: account to get its balance
        :param actual: if to use the actual or mining table
        
        :return: the balance of the given account
        """

        #get balance
        table_name = "actual_balances" if actual else "mining_balances"
        balance = self.db_safe_execute("SELECT balance from "+table_name+" where account='"+account+"'").fetchall()

        return 0 if (len(balance) == 0) else balance[0][0]

    def get_balances(self, actual=True):
        """
        Function to get balances of accounts

        :param actual: if to use the actual or mining table
        
        :return: all the balances of the either the actual or mining table
        """

        #get balance
        table_name = "actual_balances" if actual else "mining_balances"
        balances = self.db_safe_execute("SELECT * from "+table_name).fetchall()

        balances_dict = {}

        for balance in balances:
            balances_dict[balance[0]] = balance[1] 

        return balances_dict

    def account_row_exists(self, account, actual=True):
        """
        Function to check if record for account exists

        :param account: account to check
        :param actual: if to use the actual or mining table
        
        :return: boolean whether there exists a balance row for the given account
        """

        table_name = "actual_balances" if actual else "mining_balances"
        return len(self.db_safe_execute("select 1 from "+table_name+" where account='"+account+"' limit 1").fetchall()) == 1

    def __increase_balance(self, account, actual=True):
        """
        Function to increase balance of account

        :param account: account to increase its balance
        :param actual: if to use the actual or mining table
        """
        table_name = "actual_balances" if actual else "mining_balances"

        #if account exist, increment balance
        if(self.account_row_exists(account, actual)):
            self.db_safe_execute("UPDATE "+table_name+" SET balance = balance + 1 where account='"+account+"'")
        #otherwise, set balance to 1
        else:
            self.db_safe_execute("insert into  "+table_name+" (account, balance) values ('"+account+"', 1)")
        self.database.commit()

    def __decrease_balance(self, account, actual=True):
        """
        Function to decrease balance of account

        :param account: account to decrease its balance
        :param actual: if to use the actual or mining table
        """

        table_name = "actual_balances" if actual else "mining_balances"
        #if exists
        if(self.account_row_exists(account, actual)):
            #get current balance
            current_balance = self.get_balance(account, actual)
            #if has balance more than 0, decrease balance
            if current_balance > 0:
                self.db_safe_execute("UPDATE "+table_name+" SET balance = balance - 1 where account='"+account+"'")
                return 
            
        raise Exception("Not enough balance to decrease")


    def transfer(self, tx, actual=True):
        """
        Function to execute a transfer if possible

        :param tx: tx to execute
        :param actual: if to use the actual or mining table

        :return: whether successful
        """

        #get from 
        from_ac = tx.hashed_content.signed_content.from_ac
        #get to
        to_ac = tx.hashed_content.signed_content.to_ac
        #check if the sender has enough balance
        if self.get_balance(from_ac, actual) < 1 and from_ac != config.MINING_SENDER:
            return False

        #increase balance of receiver
        self.__increase_balance(to_ac, actual)

        #decrease balance of sender
        if(from_ac != config.MINING_SENDER):
            self.__decrease_balance(from_ac, actual)

        return True

    def check_transfer(self, tx, actual=True):
        """
        Function to check if a transfer is possible

        :param tx: tx to check
        :param actual: if to use the actual or mining table

        :return: whether possible
        """

        #get from 
        from_ac = tx.hashed_content.signed_content.from_ac
        #get to
        to_ac = tx.hashed_content.signed_content.to_ac
        #check if the sender has enough balance
        if self.get_balance(from_ac, actual) < 1 and from_ac != config.MINING_SENDER:
            return False

        return True

    def check_transfers(self, txs, actual=True):
        """
        Function to check if set of transfers are possible

        :param txs: txs to check
        :param actual: if to use the actual or mining table

        :return: whether possible
        """

        balances = self.get_balances()
        #for each tx
        for tx in txs:
            #get from 
            from_ac = tx.hashed_content.signed_content.from_ac
            #get to
            to_ac = tx.hashed_content.signed_content.to_ac

            if from_ac != config.MINING_SENDER:
                #check if the sender has enough balance
                if from_ac not in balances:
                    return False
                if balances[from_ac] < 1:
                    return False
                
                balances[from_ac] -= 1


            #check if exists
            if to_ac not in balances:
                balances[to_ac] = 0

            balances[to_ac] += 1

        return True

    def revert_txs(self, txs):
        """
        Function to revert txs

        :param txs: txs to revert
        """

        for tx in txs:
            #get from 
            from_ac = tx.hashed_content.signed_content.from_ac
            #get to
            to_ac = tx.hashed_content.signed_content.to_ac

            #reduce balance of receiver
            self.__decrease_balance(to_ac)

            #if not a minted tx, add balance back
            if from_ac != config.MINING_SENDER:
                self.__increase_balance(from_ac)

    def print_balances(self, actual=True):
        """
        Function to print balances

        :param actual: if to use the actual or mining table
        """

        table_name = "actual_balances" if actual else "mining_balances"
        balances = self.db_safe_execute("select * from "+table_name).fetchall()
        for balance in balances:
            print(balance[0]+": "+str(balance[1]))

    #function 
    def reset_mining_tables(self):
        """
        Function to reset mining balances
        """

        self.db_safe_execute("delete from mining_balances")
        self.db_safe_execute("insert into mining_balances select * from actual_balances")




