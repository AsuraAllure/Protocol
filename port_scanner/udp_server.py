import socket

UDP_IP = "localhost"
UDP_PORT = 111

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


while True:
    data, addr = sock.recvfrom(1024) # буфер 1024 байт
    print("Получено сообщение:", data.decode())