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
from helper_utils import write_to_file

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

    listen_UDP = threading.Thread(target=peers.process_incoming_messages, args=[protocol])
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
    # peers.broadcast_message(highest_tx_msg)

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
    global state
    global wallet

    recipient = ""
    while len(recipient) != 128:
        recipient = input("Enter address to send to: ").lower()
        if len(recipient) != 128:
            print("Username must be the initials (128 characters long)")
        if recipient == wallet.public_key:
            print("Username must be different than yours")
            recipient = ""

    if state.get_balance(wallet.public_key) < 1:
        print("Not enough balance")
        return

    # state.synchronize(protocol, peers)
        
    #get next tx number
    # next_tx_number = state.network_tx_count

    write_to_file("Sending new tx to "+recipient, state.logFile)

    #create tx 
    new_tx = Transaction(wallet.public_key, recipient)
    #sign tx
    wallet.sign_tx(new_tx)

    #add tx to state
    state.transactions.append(new_tx)

    #generate tx msg
    send_new_tx_msg = protocol.send_new_tx(new_tx)
    #send tx msg
    peers.broadcast_message(send_new_tx_msg)

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