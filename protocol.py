
from state import State

class Protocol:
    def __init__(self, state):
        self.state = state

    #function to process a message
    def process_message(self, command):

        #check command size
        if command[0] != "2":
            print("The command must start with 2")
            return

        #check last character
        if command[len(command)-1] != "3":
            print("The last character in the command must end with 3")
            return

        #make sure a size is passed
        if not command[1].isdigit() and not (command[1] == 'A' or command[1] == 'B' or command[1] == 'C' or command[1] == 'D' or command[1] == 'F' or command[1] == 'E'):
            print("The second character must be a digit or A, B, C, D, E or F - a byte indicating the number of bytes in the command")
            return
        
        #get size
        size = int(command[1],16)

        #extract command
        cmd = command[2:-1]

        #if command is longer than size
        if len(cmd) != size:
            print("The command is longer than the specified bytes")
            return

        #if got new tx
        if cmd.startswith("n"):
            #extract transaction number
            trn_hex = cmd[1:5]
            trn = int(trn_hex, 16)

            #if transaction number is more than next number, synchronise
            if trn > len(self.state.transactions) + 1:
                self.state.synchronize(self)

            #if a new height
            if (len(self.state.transactions)+1) == trn:
                #append tx
                new_tx = {
                    "number": trn,
                    "from_username": "HELLO"
                }
                return create_message("o")

            msg_to_send = self.create_message("m"+self.state.get_last_tx_height())
            return msg_to_send
        #if got highest rx height
        if cmd.startswith("h"):
            # msg_to_send = self.create_message("m"+self.state.get_last_tx_height())
            highest_tx_res = bytearray()
            highest_tx_res += "m".encode('utf-8')
            trn = self.state.get_last_tx_height()
            highest_tx_res.append(trn.to_bytes(2, byteorder='big'))
            msg_to_send = self.create_message_bytes(highest_tx_res)
            return msg_to_send
        #if got highest tx height res
        if cmd.startswith("m"):
            print("Got highest transaction result back", cmd, file=self.state.logFile)
            self.state.network_tx_count = cmd[1:len(cmd)]
        #if got okay message
        if cmd.startswith("o"):
            print("Received OK")
        #if got fail message
        if cmd.startswith("f"):
            print("Received FAIL")

    #function to process a message
    def process_message_bytes(self, message, peers):

        #check command size
        if message[0] != 2:
            print("The command must start with 2")
            return

        #check last character
        if message[len(message)-1] != 3:
            print("The last character in the command must end with 3")
            return
        
        #get size
        size = message[1]

        #extract command
        cmd = message[2:-1]

        #if command is longer than size
        if len(cmd) != size:
            print("The command is longer than the specified bytes")
            return

        #get first letter
        first_letter = chr(message[2])

        #if got new tx
        if first_letter == 'n':
            print("GOT NEW TX MSG", file=self.state.logFile)
            self.state.logFile.flush()
            #extract transaction number
            trn = int.from_bytes(cmd[1:3], byteorder='big')
            print("Got new transaction number", trn, file=self.state.logFile)
            self.state.logFile.flush()
            from_user = cmd[3:5].decode('utf-8')
            to_user = cmd[5:7].decode('utf-8')
            timestamp = int.from_bytes(cmd[7:11], byteorder='big')
            approved = int.from_bytes(cmd[11:12], byteorder='big')
            approve_tx = int.from_bytes(cmd[12:14], byteorder='big')

            #if transaction number is more than next number, synchronise
            if trn > len(self.state.transactions) + 1:
                self.state.synchronize(self, peers)
            
            #if a new height
            if (len(self.state.transactions)+1) == trn:
                #append tx
                new_tx = {
                    "number": trn,
                    "from_username": from_user,
                    "to_username": to_user,
                    "timestamp": timestamp,
                    "approved": approved,
                    "approve_tx": approve_tx
                }

                #add tx to state
                self.state.transactions.append(new_tx)
                self.state.local_tx_count += 1
                self.state.network_tx_count = len(self.state.transactions)
                #return okay
                return self.create_message_bytes("o".encode('utf-8'))
            #if height already exists
            elif len(self.state.transactions) >= trn:
                #if our stored tx is older, ignore this
                if self.state.transactions[trn-1]["timestamp"] <= timestamp:
                    #return fail
                    return self.create_message_bytes("f".encode('utf-8'))
                #if new transaction is older
                else:
                    #replace
                    self.state.transactions[trn-1] = {
                        "number": trn,
                        "from_username": from_user,
                        "to_username": to_user,
                        "timestamp": timestamp,
                        "approved": approved,
                        "approve_tx": approve_tx
                    }
                    #return ok
                    return self.create_message_bytes("o".encode('utf-8'))

        #if got highest rx height
        elif first_letter == 'h':
            print("Received query for highest tx number", file=self.state.logFile)
            self.state.logFile.flush()
            # msg_to_send = self.create_message("m"+self.state.get_last_tx_height())
            highest_tx_res = bytearray()
            highest_tx_res += "m".encode('utf-8')
            trn = self.state.get_last_tx_height()
            highest_tx_res += trn.to_bytes(2, byteorder='big')
            msg_to_send = self.create_message_bytes(highest_tx_res)
            return msg_to_send
        #if got highest tx height res
        elif first_letter == 'm':
            highest_tx = int.from_bytes(cmd[1:len(cmd)], byteorder='big')
            print("Got highest transaction result back", highest_tx, file=self.state.logFile)
            self.state.logFile.flush()
            if highest_tx > self.state.network_tx_count:
                self.state.network_tx_count = highest_tx
            #if transaction number is more than next number, synchronise
            if highest_tx > len(self.state.transactions) + 1:
                self.state.synchronize(self, peers)
        #if got get transaction
        elif first_letter == 'g':
            tx_num = int.from_bytes(cmd[1:len(cmd)], byteorder='big')
            print("Received Get transaction", tx_num, file=self.state.logFile)
            self.state.logFile.flush()
            if(tx_num <= len(self.state.transactions)):
                transaction = self.state.transactions[tx_num-1]
                print("Sending transaction", transaction["number"], file=self.state.logFile)
                self.state.logFile.flush()
                return self.send_new_tx_bytes(transaction)
        #if got okay message
        elif first_letter == 'o':
            print("Received OK", file=self.state.logFile)
            self.state.logFile.flush()
        #if got fail message
        elif first_letter == 'f':
            print("Received FAIL", file=self.state.logFile)
            self.state.logFile.flush()

    def create_message(self, message):
        #calculate message length
        msg_length = hex(len(message))[2:len(message)]

        return "2"+msg_length+message+"3"

    def get_highest_tx_num(self):
        return self.create_message_bytes(str.encode("h"))

    def create_message_bytes(self, message):
        #calculate message length
        msg_length = len(message)

        msg = bytearray()
        msg.append(2)
        msg.append(msg_length)
        msg += message
        msg.append(3)

        return msg

    def send_new_tx(self, transaction):
        #construct transaction message
        trn = str(transaction["number"])[2:len(message)]
        trtime = str(transaction["timestamp"])[2:len(message)]
        new_tx_msg = "n" + trn + transaction["from_username"] + transaction["to_username"] + trtime
        return create_message(new_tx_msg)

    def send_new_tx_bytes(self, transaction):
        #construct transaction message
        trn = transaction["number"]
        trtime = transaction["timestamp"]
        approved = transaction["approved"]
        approve_tx = transaction["approve_tx"]

        new_tx_msg = bytearray()
        new_tx_msg += "n".encode('utf-8')
        new_tx_msg += trn.to_bytes(2, byteorder='big')
        new_tx_msg += transaction["from_username"].encode('utf-8')
        new_tx_msg += transaction["to_username"].encode('utf-8')
        new_tx_msg += trtime.to_bytes(4, byteorder='big')
        new_tx_msg += approved.to_bytes(1, byteorder='big')
        new_tx_msg += approve_tx.to_bytes(2, byteorder='big')

        return self.create_message_bytes(new_tx_msg)


    def get_tx(self, trn):
        new_tx_msg = bytearray()
        new_tx_msg += "g".encode('utf-8')
        new_tx_msg += trn.to_bytes(2, byteorder='big')
        return self.create_message_bytes(new_tx_msg)