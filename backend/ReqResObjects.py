__author__ = 'rami'

class Req:

    def __init__(self, type, IPs):
        self.type = type
        self.IPs = IPs

class Res:

    def __init__(self, type, IP, port_banner):
        self.type = type
        self.IP = IP
        self.port_banner = port_banner
