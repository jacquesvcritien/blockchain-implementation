from datetime import datetime
import time
import json

class State:
    def __init__(self, port):
        self.user_initials = ""
        #array of <transaction_number, timestamp, from_username, to_username>
        self.transactions = []
        self.local_tx_count = 0
        self.network_tx_count = 0
        #read username
        self.read_username()
        self.port = port
        self.logFile = open('logs/log_'+str(port)+'.txt', 'w')

    #function to synchronize
    def synchronize(self, protocol, peers):
        highest_tx_msg = protocol.get_highest_tx_num()
        peers.broadcast_message_bytes(highest_tx_msg)
        # time.sleep(2)
        print("Current peers", len(peers.peers), file=self.logFile)
        print("Current Local txs", self.local_tx_count, file=self.logFile)
        print("Current Network txs", self.network_tx_count, file=self.logFile)
        self.logFile.flush()
        txs_behind = self.network_tx_count - self.local_tx_count
        for x in range(txs_behind):
            print("Synchronizing", file=self.logFile)
            self.logFile.flush()
            #obtain get transaction command
            get_tx_cmd = protocol.get_tx(self.local_tx_count+x+1)
            print("Getting tx", self.local_tx_count+x+1, file=self.logFile)
            self.logFile.flush()
            self.logFile.flush()
            peers.broadcast_message_bytes(get_tx_cmd)
            # self.local_tx_count += 1

    #function to read a username
    def read_username(self):
        #keep reading input until its valid 
        while len(self.user_initials) != 2:
            self.user_initials = input("Enter your username: ").upper()
            if len(self.user_initials) != 2:
                print("Username must be the initials (2 characters long)")

        print("Logged in as "+self.user_initials)

    #function to read a transaction
    def get_transaction(self, trn):
        return self.transactions[trn-1]

    #function to get the last tx height
    def get_last_tx_height(self):
        
        #if there are no transactions
        if len(self.transactions) == 0:
            return 0

        return self.transactions[len(self.transactions)-1]["number"]

    #get unapproved txs
    def get_unapproved_txs(self):
        unapproved_txs = []
        for tx in self.transactions:
            found = False
            #if transaction is not approved automatically
            if tx["approved"] == 0:
                #loop through transactions
                for tx_check in self.transactions:
                    #if transaction is found to be approved
                    if tx_check["approve_tx"] == tx["number"] and tx["to_username"]:
                        found = True
                        break
            
                #if not found to be approved
                if not found and tx["to_username"] == self.user_initials:
                    unapproved_txs.append(tx)

        return unapproved_txs
        

    #print transactions
    def print_txs(self):
        for tx in self.transactions:
            if tx["approved"] and tx["approve_tx"] != 0:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"]+" (Approval TX "+str(tx["approve_tx"])+")")
            else:
                print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"])

        self.write_txs_to_file()

    #print unapproved transactions
    def print_unapproved_txs(self):
        unapproved_txs = self.get_unapproved_txs()
        for tx in unapproved_txs:
            print(str(tx["number"])+" ("+str(datetime.fromtimestamp(tx["timestamp"]))+") : "+ tx["from_username"]+" -> "+tx["to_username"])

        self.write_txs_to_file()

    #calculates the balance of a user
    def get_balance(username):
        balance = 0
        for tx in self.transactions:
            if tx["from_username"] == username:
                balance -= 1
            elif tx["to_username"] == username and tx["approved"] == 1:
                balance += 1

        return balance

    #function to write to file
    def write_txs_to_file(self):
        jsonString = json.dumps(self.transactions)
        jsonFile = open("txs/"+str(self.port)+"_txs.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()

    #function to write unapproved txs to file
    def write_unapproved_txs_to_file(self):
        jsonString = json.dumps(self.transactions)
        jsonFile = open("txs/"+str(self.port)+"_unapproved_txs.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()


    #check if tx is approvable
    def is_tx_approvable(self, trn):
        for tx in self.transactions:
            #if transaction is not approved automatically
            if tx["number"] == trn:
                #loop through transactions
                for tx_check in self.transactions:
                    #if transaction is found to be already approved
                    if tx_check["approve_tx"] == tx["number"]:
                        return False
        
        return True

