import subprocess
import sys
import urllib
from urllib.request import urlopen
from urllib import error
from urllib.error import URLError, HTTPError
from functools import reduce
import re

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
    except urllib.error.URLError:
        return None
    else:
        return resp


def ask_regionals(ip):
    result = ask_whois_ripe(ip)
    if result == "???":
        result = ask_whois_arin(ip)
    return result


def ask_whois_ripe(ip):
    page = get_content(f'https://rest.db.ripe.net/search.json?query-string={ip}').read().decode("utf-8")
    AS_regex = r'\"(AS\d+)\"'
    AS = re.findall(AS_regex, page)
    if (not AS):
        return "???"
    return AS[0]


def ask_whois_arin(ip):
    page = get_content("https://whois.arin.net/rest/net/NET-52-84-0-0-1/pft?s=" + ip).read().decode("utf-8")
    AS_regex = r'originAS>(AS\d+)<'
    AS = re.findall(AS_regex, page)
    result_path = reduce(lambda x, y: x + " " + y, AS)
    return result_path


def get_info_about_IP(ip):
    return ask_regionals(ip)


if __name__ == "__main__":
    input = input()
    result_tracert = tracert_path(input)
    count_routing_ip = 1
    for x in result_tracert[0]:
        if is_routing_ip(x):
            info = get_info_about_IP(x)
            print(count_routing_ip, x, info)
            count_routing_ip += 1
