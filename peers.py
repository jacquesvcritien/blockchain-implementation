import time

#list of initial peers
nodes = [
    {
        "ip":"127.0.0.1",
        "port":3012
    },
    {
        "ip":"127.0.0.1",
        "port":3011
    },
]

class Peers:
    def __init__(self, socket, ip, port):
        """
        Class initialiser

        :param socket: a reference to the initialised socket
        :param ip: the ip listening on
        :param port: the port listening on
        """
        self.socket = socket
        self.peers = nodes
        self.ip = ip
        self.port = port
        self.pings = {}

    def check_in_peers(self, ip, port):
        """
        Function to check if the passed ip or port are in peers list

        :param ip: ip to check
        :param port: port to check

        :return: whether the passed in ip or port are in the peers list 
        """

        for peer in self.peers:
            if peer["ip"] == ip and peer["port"] == port:
                return True
        return False

    def add_to_peers(self, ip, port):
        """
        Function to add a peer

        :param ip: ip to add
        :param port: port to add
        """

        self.peers.append({"ip": str(ip), "port": int(port)})
        print("Added peer "+str(ip)+":"+str(port))
        print("New peers", self.peers)

    def process_incoming_messages(self, protocol):
        """
        Function to process an incoming message

        :param protocol: protocol to use
        """

        while True:
            # read msg
            data, addr = self.socket.recvfrom(65535)
            #check in peers and if not there add it
            found = self.check_in_peers(addr[0], addr[1])
            if not found:
                self.add_to_peers(addr[0], addr[1])

            #get msg start
            stx = chr(data[0])

            #process msg and get reply to send
            replies = protocol.process_message(data, self, addr[0], addr[1])

            #for each reply
            if replies:
                for reply in replies:
                    #if there is a reply
                    if reply:
                        self.broadcast_message(reply)

    def broadcast_message(self, message):
        """
        Function to broadcast a message to other peers

        :param message: message to broadcast
        """

        for peer in self.peers:
            if peer["ip"] != self.ip or peer["port"] != self.port:
                self.socket.sendto(message, (peer["ip"], peer["port"]))

    def add_pk_to_peer(self, ip, port, pk):
        """
        Function to add a public key to a peer

        :param ip: ip of peer
        :param port: port of peer
        :param pk: public key to add
        """

        found = False
        for peer in self.peers:
            if peer["ip"] == ip and peer["port"] == port:
                peer["public_key"] = pk
                found = True
        
        if not found:
            self.peers.append({ "ip":IP, "port":port, "public_key":pk })

    def received_peer_ping(self, pk):
        """
        Function to store the public key peer ping time

        :param pk: public key to store the timestamp of its ping
        """

        self.pings[pk] = int(round(time.time() * 1000))

    def check_peers(self):
        """
        Function to check if peers are active
        """

        #get time now
        milliseconds_now = int(round(time.time() * 1000))
        for ping in self.pings:
            #if more than 20 seconds since last ping, remove pk
            if self.pings[ping] + 20000 < milliseconds_now:
                for peer in self.peers:
                    if peer["public_key"] == ping:
                        del peer["public_key"]