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
import config as config

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
state = State(ip, port, chain)
protocol = Protocol(state)
wallet = None
miner = None

def check_sync():
    """
    Function to check if node is synced
    """
    global state
    #syncronize
    while True:
        state.synchronize(protocol, peers)
        #sleep for 5 seconds
        time.sleep(5)

def check_peers():
    """
    Function to check peers
    """
    global peers
    #syncronize
    while True:
        peers.check_peers()
        #sleep for 5 seconds
        time.sleep(10)

def init():
    """
    Function which runs the node
    """
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
    #set pk
    state.set_pk(wallet.public_key)
    peers.add_pk_to_peer(ip, port, wallet.public_key)
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

    #check peers every 10 seconds
    peer_check = threading.Thread(target=check_peers)
    peer_check.start()

    # transaction = Transaction("JV", "NF")
    # # transaction.calculate_hash()
    # transaction.calculate_hash_sign(wallet)

    # transaction.verify()





    # #ask for highest tx num
    # highest_tx_msg = protocol.get_highest_tx_num()
    # peers.broadcast_message(highest_tx_msg)

    # time.sleep(10)


    

init()

def check_balance():
    """
    Function to check the balance
    """

    global state
    global wallet
    print(state.database.get_balance(wallet.public_key))

#shows help
def show_help():
    """
    Function to print help
    """

    print("------ HELP ------") 
    print("check_balance: Checks the balance")
    print("send_sbb: Sends sbb")
    print("print_balances: Prints balances")
    print("print_chain: Prints the chain")
    print("print_unspent_txs: Prints unspent txs")
    print("help: Prints help")

#sends sbb
def send_sbb():
    """
    Function to send sbb
    """

    global state
    global wallet

    recipient = ""
    while len(recipient) != 128:
        recipient = input("Enter address to send to: ").lower()
        if len(recipient) != 128:
            print("Username must be the public key (128 characters long)")
        if recipient == wallet.public_key:
            print("Username must be different than yours")
            recipient = ""

    balance = state.get_balance(wallet.public_key, False)
    if balance < 1:
        print("Not enough balance")
        return

    tx_to_spend = None
    #if utxo, ask for tx hash
    if config.DB_MODEL == "utxo":
        tx_to_spend = ""
        while len(tx_to_spend) != 64:
            tx_to_spend = input("Enter tx hash to spend: ").lower()
            if len(tx_to_spend) != 64:
                print("TX Hash must be the 64 characters long")

    write_to_file("Sending new tx to "+recipient, state.logFile)

    #create tx 
    new_tx = Transaction(wallet.public_key, recipient, tx_to_spend)
    #sign tx
    wallet.sign_tx(new_tx)

    #check transfer
    transfer_possible = state.database.check_transfer(new_tx, False)
    if not transfer_possible:
        if config.MINING_TYPE == "account":
            print("Not enough balance")
        if config.MINING_TYPE == "utxo":
            print("TX Hash does not exist or is already spent")
        return

    #add tx to state
    state.add_pending_tx(new_tx)

    #perform transfer
    state.database.transfer(new_tx, False)

    #generate tx msg
    send_new_tx_msg = protocol.send_new_tx(new_tx)
    #send tx msg
    peers.broadcast_message(send_new_tx_msg)

def print_txs():
    """
    Function to print transactions
    """
    state.print_txs()

#function to print balances
def print_balances():
    """
    Function to print balances
    """
    state.database.print_balances(False)

#function to print chain
def print_chain():
    """
    Function to print chain
    """
    state.chain.print_chain()

def print_unspent_txs():
    """
    Function to print unspent txs
    """
    global wallet
    state.database.print_unspent_txs(wallet.public_key, False)

def print_txs():
    """
    Function to print transactions
    """
    state.database.print_all_txs(False)

def handleUserActions(command):
    """
    Function to handle user input

    :param command: command entered by the user
    """

    if command == "check_balance":
        check_balance()
    elif command == "send_sbb":
        send_sbb()
    elif command == "help":
        show_help()
    elif command == "print_txs":
        print_txs()
    elif command == "print_unspent_txs" and config.DB_MODEL == "utxo":
        print_unspent_txs()
    elif command == "print_balances":
        print_balances()
    elif command == "print_chain":
        print_chain()
    elif command == "print_txs":
        print_txs()

while True:
    cmd = input("\nEnter command: ")
    handleUserActions(cmd)