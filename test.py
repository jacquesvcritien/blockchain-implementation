import sqlite3

database = sqlite3.connect('dbs/test.db', check_same_thread=False)
cursor = database.cursor()

#function to print balances
def print_balances():
    balances = cursor.execute("select txs.to_ac,count(*) from unspent_txs inner join txs where unspent_txs.tx=txs.id group by txs.to_ac").fetchall()
    for balance in balances:
        print(balance[0]+": "+str(balance[1]))

cursor.execute("create table if not exists txs (id INTEGER primary key autoincrement not null, from_ac varchar(42), to_ac varchar(42))")
cursor.execute("create table if not exists unspent_txs (tx int unique REFERENCES txs(id))")
cursor.execute("insert into txs (from_ac, to_ac) values ('0000', '1111')")
cursor.execute("insert into txs (from_ac, to_ac) values ('0000', '1112')")
cursor.execute("insert into txs (from_ac, to_ac) values ('0000', '1113')")
cursor.execute("insert into txs (from_ac, to_ac) values ('0000', '1113')")
cursor.execute("insert into unspent_txs (tx) values (1)")
cursor.execute("insert into unspent_txs (tx) values (2)")
cursor.execute("insert into unspent_txs (tx) values (4)")
# cursor.execute("update txs set id = 3 where id = 1")
# print(cursor.execute("select id from txs order by id desc limit 1").fetchall())
print_balances()
print(cursor.execute("select count(*),txs.to_ac from unspent_txs inner join txs where unspent_txs.tx=txs.id group by txs.to_ac").fetchall())
# print(cursor.execute("select unspent_txs.tx,txs.to_ac from unspent_txs inner join txs where unspent_txs.tx=txs.id").fetchall())
# cursor.execute("insert into unspent_txs values(1)")
# print(cursor.execute("select * from unspent_txs inner join txs where unspent_txs.tx = txs.id and txs.to_ac = '1111'").fetchall())
# print(cursor.execute("SELECT count(*) from unspent_txs inner join txs where unspent_txs.tx = txs.id and txs.to_ac = '1111'").fetchall()[0][0])