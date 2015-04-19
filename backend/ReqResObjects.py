__author__ = 'rami'

IS_UP_BULK = "IS_UP_BULK"
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"

class Req:
    def __init__(self, type, IPs, ports = list(range(1-100))):
        self.type = type
        self.IPs = IPs
        self.ports = ports

class Res:

    def __init__(self, type, IP, port_banner):
        self.type = type
        self.IP = IP
        self.port_banner = port_banner
