import socket
import select
import os

from SNTP.message import NTP_message

class SNTP_Client:
    def __init__(self):
        pass
    def get_packet(self):
        packet = NTP_message()
        packet.LI = 0
        packet.VN = 4
        packet.mode = 3
        return packet.pack()


HOST = '127.0.0.1'
PORT = 123
TIMEOUT = 2
BUF_LEN = 1024

def main():
    s = socket.create_connection((HOST, PORT))
    s.sendall(SNTP_Client().get_packet())
    print(NTP_message().unpack(s.recv(1024)))

if __name__ == "__main__":
    main()
