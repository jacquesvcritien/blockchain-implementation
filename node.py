import socket
import sys
import threading
import time
import random
from state import State
from protocol import Protocol
from peers import Peers
from datetime import datetime
from wallet import Wallet
from transaction import Transaction
from miner import Miner
from block import Block
from chain import Chain


if len(sys.argv) == 3:
    # Get "IP address of Server" and also the "port number" from argument 1 and argument 2
    ip = sys.argv[1]
    port = int(sys.argv[2])
    print("Listening on "+str(ip)+":"+str(port))
else:
    print("Run like : python3 node.py <arg1:server ip:this system IP 192.168.1.6> <arg2:server port:4444 >")
    exit(1)

peers = []
s = None
# init chain
chain = Chain()
state = State(port, chain)
protocol = Protocol(state)
wallet = None
miner = None

def schedule_next_msg():
    global peers
    global ip
    global port
    global s

    randtime = random.randint(500, 5000)
    print("Sending in "+str(randtime)+"ms")
    time.sleep(randtime/1000)
    message = "Hello"
    peers.broadcast_message(message)

def check_sync():
    global state
    #syncronize
    while True:
        state.synchronize(protocol, peers)
        #sleep for 5 seconds
        time.sleep(5)


def init():
    global peers
    global ip
    global port
    global s
    global protocol
    global wallet
    global miner
    global chain

    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    print("Do Ctrl+c to exit the program !!")

    print("Initialising peers", file=state.logFile)
    state.logFile.flush()
    peers = Peers(s, ip, port)

    #init wallet
    wallet = Wallet(state.user_initials)
    #init miner
    miner = Miner(wallet, chain, state, protocol, peers)

    #sync every 5 seconds
    syncing_check = threading.Thread(target=check_sync)
    syncing_check.start()

    listen_UDP = threading.Thread(target=peers.process_incoming_messages_bytes, args=[protocol])
    listen_UDP.start()

    time.sleep(5)

    mining = threading.Thread(target=miner.run, args=[])
    mining.start()

    # transaction = Transaction("JV", "NF")
    # # transaction.calculate_hash()
    # transaction.calculate_hash_sign(wallet)

    # transaction.verify()





    # #ask for highest tx num
    # highest_tx_msg = protocol.get_highest_tx_num()
    # peers.broadcast_message_bytes(highest_tx_msg)

    # time.sleep(10)


    

init()


#check balance
def check_balance():
    print("Balance of "+str(state.user_initials)+" is: "+str(get_balance())+" WBE")

#shows help
def show_help():
    print("------ HELP ------") 
    print("check_balance: Checks the balance")
    print("send_wbe: Sends WBE")
    print("send_wbe_approval: Sends WBE with approval from receiver")
    print("help: Prints help")
    print("print_txs: Prints transactions")

#sends wbe
def send_wbe():
    username = ""
    while len(username) != 2:
        username = input("Enter username to send to: ").upper()
        if len(username) != 2:
            print("Username must be the initials (2 characters long)")
        if username == state.user_initials:
            print("Username must be different than yours")
            username = ""

    if get_balance() < 1:
        print("Not enough balance")
        return

    state.synchronize(protocol, peers)
        
    #get next tx number
    next_tx_number = state.network_tx_count
    print("Sending new tx "+str(next_tx_number+1), file=state.logFile)
    state.logFile.flush()

    transaction = {
        "number": next_tx_number+1,
        "from_username": state.user_initials,
        "to_username": username,
        "timestamp": int(time.time()),
        "approved": 1,
        "approve_tx": 0
    }

    #add transaction
    state.transactions.append(transaction)
    state.local_tx_count += 1
    state.network_tx_count += 1

    #generate tx msg
    send_new_tx_msg = protocol.send_new_tx_bytes(transaction)
    #send tx msg
    peers.broadcast_message_bytes(send_new_tx_msg)

#sends wbe
# def approve_transaction():
#     trn = ""
#     valid = False
#     while not valid:
#         trn = input("Enter transaction number: ")
#         if not trn.isnumeric():
#             print("Transaction number must be a valid number")
#             continue

#         trn = int(trn)
#         if trn > len(state.transactions) or trn < 1:
#             print("Transaction does not exist")
#             continue

#         #get transaction
#         tx = state.get_transaction(trn)

#         #check if user can approve
#         if tx["to_username"] != state.user_initials:
#             print("Unauthorized")
#             continue

#         #check if tx is already approved
#         if not state.is_tx_approvable(trn):
#             print("Transaction is already approved")
#             continue

#         valid = True

#     state.synchronize(protocol, peers)
        
#     #get next tx number
#     next_tx_number = state.network_tx_count
#     print("Sending new tx "+str(next_tx_number+1), file=state.logFile)
#     state.logFile.flush()

#     transaction = {
#         "number": next_tx_number+1,
#         "from_username": "00",
#         "to_username": state.user_initials,
#         "timestamp": int(time.time()),
#         "approved": 1,
#         "approve_tx": trn
#     }

#     #add transaction
#     state.transactions.append(transaction)
#     state.local_tx_count += 1
#     state.network_tx_count += 1

#     #generate tx msg
#     send_new_tx_msg = protocol.send_new_tx_bytes(transaction)
#     #send tx msg
#     peers.broadcast_message_bytes(send_new_tx_msg)

# #sends wbe with approval
# def send_wbe_approval():
#     username = ""
#     while len(username) != 2:
#         username = input("Enter username to send to: ").upper()
#         if len(username) != 2:
#             print("Username must be the initials (2 characters long)")
#         if username == state.user_initials:
#             print("Username must be different than yours")
#             username = ""

#     if get_balance() < 1:
#         print("Not enough balance")
#         return

#     state.synchronize(protocol, peers)
        
#     #get next tx number
#     next_tx_number = state.network_tx_count
#     print("Sending new tx "+str(next_tx_number+1), file=state.logFile)
#     state.logFile.flush()

#     transaction = {
#         "number": next_tx_number+1,
#         "from_username": state.user_initials,
#         "to_username": username,
#         "timestamp": int(time.time()),
#         "approved": 0,
#         "approve_tx": 0
#     }

#     #add transaction
#     state.transactions.append(transaction)
#     state.local_tx_count += 1
#     state.network_tx_count += 1

#     # print(transaction)

#     #generate tx msg
#     send_new_tx_msg = protocol.send_new_tx_bytes(transaction)
#     #send tx msg
#     peers.broadcast_message_bytes(send_new_tx_msg)

def print_txs():
    state.print_txs()

#function to print balances
def print_balances():
    state.database.print_balances()

#function to print chain
def print_chain():
    state.chain.print_chain()

def print_unapproved_txs():
    state.print_unapproved_txs()

def get_balance():
    balance = 0
    for tx in state.transactions:
        if tx["from_username"] == state.user_initials:
            balance -= 1
        elif tx["to_username"] == state.user_initials and tx["approved"] == 1:
            balance += 1

    return balance


#function to handle user actions
def handleUserActions(command):
    if command == "check_balance":
        check_balance()
    elif command == "send_wbe":
        send_wbe()
    elif command == "send_wbe_approval":
        send_wbe_approval()
    elif command == "help":
        show_help()
    elif command == "print_txs":
        print_txs()
    elif command == "print_unapproved_txs":
        print_unapproved_txs()
    elif command == "approve_tx":
        approve_transaction()
    elif command == "print_balances":
        print_balances()
    elif command == "print_chain":
        print_chain()

while True:
    cmd = input("\nEnter command: ")
    handleUserActions(cmd)