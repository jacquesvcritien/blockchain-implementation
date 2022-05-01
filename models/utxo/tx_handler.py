#function to handle a transaction using the account model
def handle_transaction(tx):
    #extract transaction number
    trn = int.from_bytes(cmd[1:3], byteorder='big')
    print("Got new transaction number", trn, file=self.state.logFile)
    self.state.logFile.flush()
    from_user = cmd[3:5].decode(config.BYTE_ENCODING_TYPE)
    to_user = cmd[5:7].decode(config.BYTE_ENCODING_TYPE)
    timestamp = int.from_bytes(cmd[7:11], byteorder='big')
    approved = int.from_bytes(cmd[11:12], byteorder='big')
    approve_tx = int.from_bytes(cmd[12:14], byteorder='big')

        #if transaction number is more than next number, synchronise
    if trn > len(self.state.transactions) + 1:
        self.state.synchronize(self, peers)

    payload_received = cmd[1:len(cmd)].decode(config.BYTE_ENCODING_TYPE)
    print("received new block", payload_received)
    #change to json
    payload_received = json.load(payload_received)