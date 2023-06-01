import socket
import ssl
import multiprocessing
import threading
from SNTP.message import NTP_message
from DNS_SERVER.Message.Messages import DNS_MESSAGE
import signal

def check_udp_connection(host, port):
    if HOST != 'localhost':
        return False
    is_open = False
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(2)
    try:
        udp_socket.sendto(b'bla-bla-bla', (host, port))
        data , _ = udp_socket.recvfrom(1024)
        # Если что-то ответили, то очевидно, что открыт порт
        is_open = True
    except socket.timeout:
        # Нет разрыва сообщение через icmp сообщение
        is_open = True
    except ConnectionError:
        pass
    finally:
        udp_socket.close()
    return is_open


def check_tcp_connection(host, port):
    is_open = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(2)
        sock.connect((host, port))
        is_open = True
    except Exception:
        is_open = False
    finally:
        sock.close()
    return is_open

def check_range(start, end):
    for port in range(start, end + 1):
        if check_tcp_connection(HOST, port):
            opened_tcp_ports.append(port)
        if check_udp_connection(HOST, port):
            opened_udp_ports.append(port)


# pop.yandex.ru 995
# smtp.yandex.ru 465
# yandex.ru 80
# ns1.google.com 53

MAX_COUNT_THREADS = 64
START_INDEX = 10
END_INDEX = 100
# IP-адрес и порт, к которому нужно подключиться
HOST = 'ns1.google.com'

opened_tcp_ports = []
opened_udp_ports = []

count_ports =  END_INDEX - START_INDEX + 1
count_thread = count_ports

if count_thread > MAX_COUNT_THREADS:
    count_thread = MAX_COUNT_THREADS

borders = []
left_border = START_INDEX

step = count_ports // count_thread
ost = count_ports % count_thread

for x in range(count_thread):
    r_border = left_border + step - 1
    if ost != 0:
        r_border += 1
        ost -= 1
    bord = (left_border, r_border)
    borders.append(bord)
    left_border = r_border + 1

threads = []
for bord in borders:
    thread_tcp_check = threading.Thread(target=check_range, args=(bord[0], bord[1]))
    threads.append(thread_tcp_check)
    thread_tcp_check.start()

for t in threads:
    t.join()

opened_tcp_ports.sort()
opened_udp_ports.sort()
print("TCP: ", opened_tcp_ports)
print("UDP: ", opened_udp_ports)

# UDP Protocols: SNTP, DNS
# TCP Protocols: DNS, POP3, SMTP, HTTP

#DNS
def standart_query(domain_name, type):
    mes = b'\x9b\xce\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    for x in domain_name.split("."):
        mes += len(x).to_bytes(1, "big", signed=False) + x.encode()
    mes += b"\x00"
    mes += type.to_bytes(2, "big", signed=False) + b'\x00\x01'
    return mes


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = ''
    while True:
        data = socket.recv(1024)
        recv_data += data.decode()
        if not data or len(data) < 1024:
            break
    return recv_data



# HTTP
def get_prepared_message(data):
    message = data['method'] + ' ' + data['url'] + ' ' \
              + 'HTTP/' + data['version'] + '\n'
    for header, value in data['headers'].items():
        message += f'{header}: {value}\n'
    if data['body']:
        pass
    message += '\n'
    return message


# Secured connections
def check_SMTP_POP3(port, sock):
    try:
        with ssl_contex.wrap_socket(sock, server_hostname=HOST) as client:
            # Проверим на pop3 and smtp, в них сервера отвечают первыми.
            client.settimeout(1)
            data = client.recv(1024).decode('utf-8')
            if data.startswith('220') or data.startswith('554'):
                protocols_on_port[(port, "TCP")] = "SMTP"
                is_SMTP_POP3 = True
            if data.startswith('+OK'):
                protocols_on_port[(port, "TCP")] = "POP3"
                is_SMTP_POP3 = True
    except (socket.timeout, ConnectionError, ssl.SSLError):
        pass

ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_contex.check_hostname = False
ssl_contex.verify_mode = ssl.CERT_NONE

is_SMTP_POP3 = False
protocols_on_port = {}

for port in opened_tcp_ports:
    is_SMTP_POP3 = False
    # Check DNS
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(standart_query('yanasfsfasfdex.ru', 111), (HOST, port))
    udp_socket.settimeout(5)
    try:
        data, server = udp_socket.recvfrom(4096)
        message = DNS_MESSAGE()
        message.unpack(data)
        if message.header.RCODE != 0 and message.header.QR == 1 and message.header.Z == 0 and message.header.ID == 39886:
            protocols_on_port[(port, "UDP/TCP")] = "DNS"
            continue
    except (socket.timeout, ConnectionError):
        pass
    udp_socket.close()

    message = get_prepared_message(
        {
            'method': 'GETt',
            'url': '/',
            'version': '1.1',
            'headers': {'host': HOST},
            'body': None
        }
    )
    # Проверим на HTTP
    try:
        with socket.create_connection((HOST, port)) as client_socket:
            client_socket.settimeout(5)
            client_socket.send(message.encode())
            data = client_socket.recv(65535).decode('cp1251')
            if data.startswith('HTTP/'):
                protocols_on_port[(port, "TCP")] = "HTTP"
                continue
    except (socket.timeout, ConnectionError):
        pass


    #Check POP3 SMTP secured
    with socket.create_connection((HOST, port)) as sock:
        p = threading.Thread(target=check_SMTP_POP3, args=(port, sock))
        p.start()
        p.join(10)
        sock.close()
        if is_SMTP_POP3:
            continue

    #Check POP3 SMTP Without secure
    try:
        with socket.create_connection((HOST, port)) as client:
            client.settimeout(3)
            data = client.recv(1024).decode('utf-8')
            if data.startswith('220') or data.startswith('554'):
                protocols_on_port[(port, "TCP")] = "SMTP"
            if data.startswith('+OK'):
                protocols_on_port[(port, "TCP")] = "POP3"
    except (socket.timeout, ConnectionError): pass
print(protocols_on_port)

for port in opened_udp_ports:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b'\x1b' + 47 * b'\0'  # формирование запроса в бинарном виде
        client.settimeout(5)
        client.sendto(data, (HOST, port))
        data, address = client.recvfrom(1024)  # получение ответа от сервера
        if data:
            sntp_time = struct.unpack('!12I', data)[10]  # извлечение информации о времени
            sntp_time -= 2208988800  # коррекция смещения времени
            if abs(int(time.time()) - sntp_time) < 10 :
                protocols_on_port[(port,'UDP')] = "SNTP"
    except (socket.timeout, ConnectionError, Exception):
        pass

