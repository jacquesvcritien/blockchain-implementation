
import sqlite3

class Database:
    def __init__(self, port):
        self.database = sqlite3.connect('dbs/'+str(port)+'_db_utxo.db', check_same_thread=False)
        self.cursor = self.database.cursor()

        #create tables if they do not exist
        self.cursor.execute("create table if not exists txs (id integer primary key autoincrement, from_ac varchar(42) not null, to_ac varchar(42) not null, spent_tx integer not null)")
        self.cursor.execute("create table if not exists mining_txs (id integer primary key autoincrement, from_ac varchar(42) not null, to_ac varchar(42) not null, spent_tx integer not null)")
        self.cursor.execute("create table if not exists unspent_txs (tx integer unique REFERENCES txs(id) not null)")
        self.cursor.execute("create table if not exists mining_unspent_txs (tx integer unique REFERENCES txs(id) not null)")
        # self.cursor.execute("create table if not exists unspent_txs (id int primary key, tx int unique REFERENCES txs(id))")

    #function to get balance of account
    def get_balance(self, account, actual=True):
        #get balance
        table_name = "unspent_txs" if actual else "mining_unspent_txs"
        #get balance
        balance = self.cursor.execute("SELECT count(*) from "+table_name+" inner join txs where unspent_txs.tx = txs.id and txs.to_ac = "+account).fetchall()[0][0]
        return balance

    #function to get last tx id
    def get_last_tx_id(self, actual=True):
        txs_table_name = "txs" if actual else "mining_txs"
        return cursor.execute("select id from "+txs_table_name+" order by id desc limit 1").fetchall()[0][0]

    #function to execute a transfer if possible
    def transfer(self, tx_num, from_ac, to, actual=True):
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"

        #check if the sender has an unspent tx
        # unspent_txs = self.cursor.execute("SELECT * from unspent_txs inner join txs where to_ac = "+from_ac).fetchall()
        unspent_txs = self.cursor.execute("SELECT count(*) from "+unspent_table_name+" where tx = "+tx_num).fetchall()[0][0]
        if unspent_txs < 1 and from_ac != "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000":
            return False

        #add new tx
        cursor.execute("insert into "+txs_table_name+" (from_ac, to_ac, spent_tx) values ("+from_ac+","+to+","+str(tx_num)+")")

        #get last tx id
        last_id = self.get_last_tx_id(actual)

        #if sender is 0, create unspent tx, otherwise update
        if(from_ac == "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"):
            cursor.execute("insert into "+unspent_table_name+" (tx) values ("+str(last_id)+")")
        else:
            cursor.execute("update "+unspent_table_name+" set tx="+str(last_id)+" where tx="+str(tx_num))


    #function to check if a transfer is possible
    def check_transfer(self, tx_num, from_ac, actual=True):
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        #check if the sender has an unspent tx with that number
        return cursor.execute("select count(*) from "+unspent_table_name+" inner join "+txs_table_name+" where "+unspent_table_name+".tx = "+txs_table_name+".id and "+unspent_table_name+".tx = "+str(tx_num)+" and "+txs_table_name+".from_ac = "+from_ac)[0][0] > 0

    #function to print balances
    def print_balances(self, actual=True):
        unspent_table_name = "unspent_txs" if actual else "mining_unspent_txs"
        txs_table_name = "txs" if actual else "mining_txs"
        balances = cursor.execute("select "+unspent_table_name+".to_ac,count(*) from "+unspent_table_name+" inner join "+unspent_table_name+" where "+unspent_table_name+".tx="+unspent_table_name+".id group by "+unspent_table_name+".to_ac").fetchall()
        for balance in balances:
            print(balance[0]+": "+str(balance[1]))

    #function to reset mining balances
    def reset_mining_table(self):
        self.cursor.execute("delete from mining_unspent_txs")
        self.cursor.execute("delete from mining_txs")
        self.cursor.execute("insert into mining_unspent_txs select * from unspent_txs")
        self.cursor.execute("insert into mining_txs select * from txs")