import json
import subprocess
import sys
import urllib
from urllib.request import urlopen
from urllib import error
from urllib.error import URLError, HTTPError
from functools import reduce
import re
import socket



def extractIp(trace):
    formattedTrace1 = [x for x in trace.split("\r\n") if x and x.startswith(" ")]
    formattedTrace1 = [x.split()[-1] for x in formattedTrace1 if "Request timed out." not in x and "\r" not in x]
    for i in range(len(formattedTrace1)):
        if (formattedTrace1[i].startswith('[')):
            formattedTrace1[i] = formattedTrace1[i][1:-1]
    return ([x.split()[-1] for x in formattedTrace1], trace.replace("\r\n", "\n"))


def tracert_path(ip):
    trace_rt_info = subprocess.run("tracert " + ip, shell=True, capture_output=True)
    return extractIp(trace_rt_info.stdout.decode("utf-8"))


def is_routing_ip(ip):
    ip = ip.split(".")
    if (ip[0] == "10" or
            (ip[0] == "172" and int(ip[1]) in range(16, 32)) or
            (ip[0] == "192" and ip[1] == "168")):
        return False
    return True


def get_content(name):
    try:
        resp = urlopen(name, data=None, timeout=10)
    except urllib.error.URLError as e:
        return None
    else:
        return resp


def ask_regionals(ip):
    result = "???",""
    try:
        result = ask_db_ripe(ip), "ripe"
    except AttributeError:
        result = "???", "ripe"

    if result[0] == "???":
        result = ask_whois_server(ip, "whois.arin.net", r'OriginAS:\s+(AS\d+)'), 'arin'
    if result[0] == "???":
        result = ask_whois_server(ip, "whois.lacnic.net",  r'aut-num:\s+(AS\d+)'), "lacnic"
    if result[0] == "???":
        result = ask_whois_server(ip, "whois.apnic.net", r'\b(AS\d+)\b'), "apnic"
    if result[0] == "???":
        result = ask_whois_server(ip, "whois.afrinic.net", r'\b(AS\d+)\b'), "afrinic"
    return result

def ask_db_ripe(ip):
    page = get_content(f'https://rest.db.ripe.net/search.json?query-string={ip}').read().decode("utf-8")
    AS_regex = r'\"(AS\d+)\"'
    AS = re.findall(AS_regex, page)
    if (not AS):
        return "???"
    return AS[0]

def ask_whois_server(ip, name_server, regex):
    page = whois_query(ip, name_server)
    AS_regex = regex
    AS = re.findall(AS_regex, page)
    if AS == []:
        return "???"
    return AS[0]

def whois_query(ip, whois_host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((whois_host, 43))
    query = ip + '\r\n'
    sock.send(query.encode())
    response = ''
    while True:
        data = sock.recv(4096).decode()
        response += data
        if not data:
            break
    sock.close()
    return response


def ask_ipinfo(ip):
    try:
        page = json.load(get_content(r"https://ipinfo.io/"+ip+"/json"))
    except AttributeError:
        return "???"
    try:
        answer = page["org"]
    except KeyError:
        answer = ""
    as_regex = r"\b(AS\d+)\b"
    answer = re.findall(as_regex, answer)
    if answer == []:
        answer = "???"
    else:
        answer = answer[0]
    return answer, "ipinfo"

def get_info_about_IP(ip):
    answer = ask_regionals(ip)
    if (answer[0] == "???"):
        answer = ask_ipinfo(ip)
    return answer


if __name__ == "__main__":
    #print(whois_query("109.244.194.121", "whois.apnic.net"))

    input = input()
    result_tracert = tracert_path(input)
    count_routing_ip = 1
    if "unreachable." in result_tracert:
        print("tracert unreachable.")
    else:
        for x in result_tracert[0]:
            if is_routing_ip(x):
                info = get_info_about_IP(x)
                print(count_routing_ip, x, info)
                count_routing_ip += 1



"""
https://query.milacnic.lacnic.net/search?id=161.148.125.40
"""

"""
vk.com
1 217.148.63.115 AS31499
2 85.112.122.5 AS25478
3 87.240.132.67 AS47541

"""

"""
tencent.com
1 217.148.63.117 (('AS31499', 'ripe'), 'regionals')
2 85.112.122.13 (('AS25478', 'ripe'), 'regionals')
3 81.173.21.1 (('AS4134', 'ripe'), 'regionals')
4 202.97.64.166 ('AS4134', 'ipinfo')
5 113.96.5.205 ('AS4134', 'ipinfo')
6 14.18.199.106 ('AS4134', 'ipinfo')
7 109.244.194.121 ('AS45090', 'ipinfo')
"""

"""
google.com
1 217.148.63.117 AS31499
2 194.226.100.138 ???
3 74.125.244.180 AS15169
4 72.14.232.85 AS15169
5 142.251.51.187 AS15169
6 172.253.51.187 AS15169
7 173.194.222.101 AS15169
"""

"""
gov.br
1 217.148.63.141 (('AS31499', 'ripe'), 'regionals')
2 90.151.170.97 (('AS35400', 'ripe'), 'regionals')
3 87.226.133.51 (('AS12389', 'ripe'), 'regionals')
4 213.249.107.129 (('AS3356', 'ripe'), 'regionals')
5 4.69.215.105 (('???', 'lacnic'), 'regionals')
6 8.242.4.210 (('???', 'lacnic'), 'regionals')
7 161.148.125.40 (('AS10954', 'lacnic'), 'regionals')"""


""" 
remarks:         AFRINIC (Africa)
remarks:         http://www.afrinic.net/ whois.afrinic.net
remarks:         
remarks:         APNIC (Asia Pacific)
remarks:         http://www.apnic.net/ whois.apnic.net
remarks:         
remarks:         ARIN (Northern America)
remarks:         http://www.arin.net/ whois.arin.net
remarks:         
remarks:         LACNIC (Latin America and the Carribean)
remarks:         http://www.lacnic.net/ whois.lacnic.net
"""