
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 65535)
s.bind(server_address)
s.sendto(message.encode('utf-8'), ("127.0.0.1", 3033))

while True:
    # read msg
    data, addr = .recvfrom(1024)
    msg_received = data.decode('utf-8')