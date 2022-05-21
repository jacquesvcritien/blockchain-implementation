
import sqlite3
import config as config
import threading

class Database:
    def __init__(self, port):
        self.database = sqlite3.connect('dbs/'+str(port)+'_db_utxo.db', check_same_thread=False)
        self.database.execute("PRAGMA foreign_keys = ON;")

        self.cursor = self.database.cursor()

        self.lock = threading.Lock()

        #create tables if they do not exist
        self.db_safe_execute("create table if not exists txs (hash varchar(64) primary key, from_ac varchar(42) not null, to_ac varchar(42) not null, spent_tx varchar(64) not null)")
        self.db_safe_execute("create table if not exists mining_txs (hash varchar(64) primary key, from_ac varchar(42) not null, to_ac varchar(42) not null, spent_tx varchar(64) not null)")
        self.db_safe_execute("create table if not exists unspent_txs (tx varchar(64) unique REFERENCES txs(hash) not null)")
        self.db_safe_execute("create table if not exists mining_unspent_txs (tx varchar(64) unique REFERENCES mining_txs(hash) not null)")

    #function to execute commands with lock
    def db_safe_execute(self, command):
        try:
            self.lock.acquire(True)
            return self.cursor.execute(command)
        finally:
            self.lock.release()

    #function to get balance of account
    def get_balance(self, account, actual=True):
        #get balance
        table_name = "unspent_txs" if actual else "mining_unspent_txs"
        #get balance
        balance = self.db_safe_execute("SELECT count(*) from "+table_name+" inner join txs where unspent_txs.tx = txs.hash and txs.to_ac = '"+account+"'").fetchall()[0][0]
        return balance

    #function to get balance of account
    def get_balances(self, actual=True):
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        unspent_txs = self.db_safe_execute("select "+txs_table_name+".to_ac,"+unspent_table_name+".tx from "+unspent_table_name+" inner join "+txs_table_name+" where "+unspent_table_name+".tx="+txs_table_name+".hash group by "+txs_table_name+".to_ac").fetchall()

        balances_dict = {}

        #loop through all unspent txs
        for unspent_tx in unspent_txs:
            #if user is not in list, add the user
            if unspent_tx[0] not in balances_dict:
                balances_dict[unspent_tx[0]] = []

            #append unspent tx to user
            balances_dict[unspent_tx[0]].append(unspent_tx[1])

        return balances_dict

    #function to execute a transfer if possible
    def transfer(self,tx, actual=True):
        #get from
        from_ac = tx.hashed_content.signed_content.from_ac
        #get to
        to_ac = tx.hashed_content.signed_content.to_ac
        #get spent tx
        spent_tx = tx.hashed_content.signed_content.spent_tx

        #choose tables to user
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs" 

        #check if the sender has an unspent tx
        # unspent_txs = self.cursor.execute("SELECT * from unspent_txs inner join txs where to_ac = "+from_ac).fetchall()
        unspent_txs = self.db_safe_execute("SELECT count(*) from "+unspent_table_name+" where tx = '"+spent_tx+"'").fetchall()[0][0]
        if unspent_txs < 1 and from_ac != config.MINING_SENDER:
            return False

        #add new tx
        self.db_safe_execute("insert into "+txs_table_name+" (hash, from_ac, to_ac, spent_tx) values ('"+tx.hash+"','"+from_ac+"','"+to_ac+"','"+spent_tx+"')")

        #if sender is 0, create unspent tx, otherwise update
        if(from_ac == config.MINING_SENDER):
            self.db_safe_execute("insert into "+unspent_table_name+" (tx) values ('"+tx.hash+"')")
        else:
            self.db_safe_execute("update "+unspent_table_name+" set tx='"+tx.hash+"' where tx='"+spent_tx+"'")


    #function to check if a transfer is possible
    def check_transfer(self, tx, actual=True):
        #get from 
        from_ac = tx.hashed_content.signed_content.from_ac
        #get to
        to_ac = tx.hashed_content.signed_content.to_ac
        #get spent tx
        spent_tx = tx.hashed_content.signed_content.spent_tx
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        #check if the sender has an unspent tx with that number
        mined_tx = from_ac == config.MINING_SENDER

        if not mined_tx:
            self.print_mining_tables(from_ac)
        
        #check if sender can spend the unspent tx
        has_unspend_tx = self.db_safe_execute("select count(*) from "+unspent_table_name+" inner join "+txs_table_name+" where "+unspent_table_name+".tx = "+txs_table_name+".hash and "+unspent_table_name+".tx = '"+spent_tx+"' and "+txs_table_name+".to_ac = '"+from_ac+"'").fetchall()[0][0] < 1
        if(has_unspend_tx and not mined_tx):
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

            if from_ac != config.MINING_SENDER:
                #check if the sender has enough balance
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
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        balances = self.db_safe_execute("select "+txs_table_name+".to_ac,count(*) from "+unspent_table_name+" inner join "+txs_table_name+" where "+unspent_table_name+".tx="+txs_table_name+".hash group by "+txs_table_name+".to_ac").fetchall()
        for balance in balances:
            print(balance[0]+": "+str(balance[1]))

    #function to print unspent txs
    def print_unspent_txs(self, account, actual=True):
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        unspent_txs = self.db_safe_execute("select "+unspent_table_name+".tx from "+unspent_table_name+" inner join "+txs_table_name+" where "+unspent_table_name+".tx="+txs_table_name+".hash and "+txs_table_name+".to_ac = '"+account+"'").fetchall()
        for tx in unspent_txs:
            print(tx[0])

    #function to print all txs
    def print_all_txs(self, actual=True):
        txs_table_name = "txs" if actual else "mining_txs"
        print(self.db_safe_execute("select * from "+txs_table_name).fetchall())

    def print_mining_tables(self, sender):
        all_txs = self.db_safe_execute("select * from mining_txs").fetchall()
        print("all txs")
        for tx in all_txs:
            print("Hash", tx[0])
            print("From", tx[1])
            print("To", tx[2])
            print("Spent", tx[3])
            print()

        self.print_unspent_txs(sender, False)

    #function to reset mining balances
    def reset_mining_tables(self):
        self.db_safe_execute("delete from mining_unspent_txs")
        self.db_safe_execute("delete from mining_txs")
        self.db_safe_execute("insert into mining_txs select * from txs")
        self.db_safe_execute("insert into mining_unspent_txs select * from unspent_txs")

    #function to remove txs for replacing block
    def remove_txs(self, txs):

        sql_clause_txs = "("
        sql_clause_spent_txs = "("
        for tx in txs:
            sql_clause_txs += (tx.hash+",")
            sql_clause_spent_txs += (tx.hashed_content.signed_content.spent_tx+",")

        sql_clause_txs = sql_clause_txs[:-1]
        sql_clause_spent_txs = sql_clause_spent_txs[:-1]
        sql_clause_txs += ")"
        sql_clause_spent_txs += ")"

        self.db_safe_execute("delete from unspent_txs where tx in "+sql_clause_spent_txs)
        self.db_safe_execute("delete from txs where hash in "+sql_clause_txs)

    #function to add unspect txs for replacing block
    def add_unspent_txs(self, unspent_balances):

        for balance in unspent_balances:
            for tx in unspent_balances[balance]:
                self.db_safe_execute("insert into unspent_txs (tx) values ('"+tx+"')")