nodes = [
    {
        "ip":"127.0.0.1",
        "port":3012
    },
    {
        "ip":"127.0.0.1",
        "port":3013
    },
]

class Peers:
    def __init__(self, socket, ip, port):
        self.socket = socket
        self.peers = nodes
        self.ip = ip
        self.port = port

    def check_in_peers(self, ip, port):
        for peer in self.peers:
            if peer["ip"] == ip and peer["port"] == port:
                return True
        return False

    def add_to_peers(self, ip, port):
        self.peers.append({"ip": str(ip), "port": int(port)})
        print("Added peer "+str(ip)+":"+str(port))
        print("New peers", self.peers)


    def process_incoming_messages(self, protocol):
        while True:
            # read msg
            data, addr = self.socket.recvfrom(1024)
            msg_received = data.decode('utf-8')
            # print("RECEIVED: "+msg_received+" FROM "+str(addr[0])+":"+str(addr[1]))
            #check in peers and if not there add it
            found = self.check_in_peers(addr[0], addr[1])
            if not found:
                self.add_to_peers(addr[0], addr[1])

            #process msg and get reply to send
            reply = protocol.process_message(msg_received)

            #if there is a reply
            if reply:
                self.broadcast_message(reply)

    def process_incoming_messages_bytes(self, protocol):
        while True:
            # read msg
            data, addr = self.socket.recvfrom(1024)
            # print("RECEIVED: "+str(data)+" FROM "+str(addr[0])+":"+str(addr[1]))
            #check in peers and if not there add it
            found = self.check_in_peers(addr[0], addr[1])
            if not found:
                self.add_to_peers(addr[0], addr[1])

            #process msg and get reply to send
            reply = protocol.process_message_bytes(data, self)

            #if there is a reply
            if reply:
                self.broadcast_message_bytes(reply)

    def discover_other_nodes(self):
        print("Discovering")


    def broadcast_message(self, message):
        for peer in self.peers:
            if peer["ip"] != self.ip or peer["port"] != self.port:
                self.socket.sendto(message.encode('utf-8'), (peer["ip"], peer["port"]))
                print("SENT: ", message, "TO ", peer)

    def broadcast_message_bytes(self, message):
        for peer in self.peers:
            if peer["ip"] != self.ip or peer["port"] != self.port:
                self.socket.sendto(message, (peer["ip"], peer["port"]))
                # print("SENT: ", str(message), "TO ", peer)