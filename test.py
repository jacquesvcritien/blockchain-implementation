from state import State
from protocol import Protocol

state = State()
protocol = Protocol(state)
cmd = ""

#check balance
def check_balance():
    print("Checking balance")

#shows help
def show_help():
    print("------ HELP ------") 
    print("check_balance: Checks the balance")
    print("send_wbe: Sends WBE")

#sends wbe
def send_wbe():
    print("Sending WBE")

#handle other commands
def handle_commands(command):
    
    result = protocol.process_message(command)
    print("Result", result)
    


#function to handle user actions
def handleUserActions(command):
    if command == "check_balance":
        check_balance()
    elif command == "send_wbe":
        send_wbe()
    elif command == "help":
        show_help()
    else:
        handle_commands(command)

while True:
    cmd = input("\nEnter command: ")
    handleUserActions(cmd)

