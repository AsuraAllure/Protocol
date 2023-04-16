from SNTP.message import NTP_message
from time import time
from SNTP.message import time_1900_1970
from math import modf
import socket
import os
import time
import smtplib

class SNTP_Server:
    def __init__(self):
        with open("config.txt") as file:
            self.delay = int(file.read())

    def answer(self, input: NTP_message) -> NTP_message:
        input.LI = 0
        input.stratum = 1
        if input.mode == 3:
            input.mode = 4
        else:
            input.mode = 2
        input.root_delay = 0
        input.root_dispersion = 0
        input.precison = -6
        input.reference_id = b'VLF\x00'
        t = time.time() + time_1900_1970 + self.delay
        frac, whole = modf(t)
        whole = int(whole)
        frac = int(str(frac)[2:11])
        time_tmstmp =( whole << 32 ) | frac
        input.receive_tmstmp = time_tmstmp
        input.reference_tmstmp = time_tmstmp
        input.transmit_tmstmp = time_tmstmp
        return input.pack()



HOST = '127.0.0.1'
PORT = 123

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    server = SNTP_Server()

    while True:
        # Программа будет останавливаться в этой точке до получения входящего соединения. Когда это произойдет, серверный сокет создаст новый сокет, который будет использоваться на данной машине для связи с клиентом. Этот новый сокет представлен объектом conn, который возвращается вызовом accept(). Объект addr содержит IP адрес и номер порта удаленной машины.
        conn, addr = s.accept()
        res = conn.recv(1024)
        inp = NTP_message().unpack(res)
        print(inp)
        data = server.answer(inp)
        conn.sendall(data)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


if __name__ == "__main__":
    main()
