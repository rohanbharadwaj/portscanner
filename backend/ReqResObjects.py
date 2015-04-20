__author__ = 'rami'

IS_UP_BULK = "IS_UP_BULK"
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"

class Req:
    def __init__(self, type, IPs, ports = list(range(1, 100))):
        self.type = type
        self.IPs = IPs
        self.ports = ports

class Job(Req):
	def __init__(self, type, IPs, startPort, endPort, jobId=None, reqId=None):
		ports = list(range(startPort, endPort+1)
		super(type, IPs, ports)
		self.jobId = jobId
		self.reqId = reqId

class Register:
	def __init__(self, IP, port):
		self.IP = IP
		self.port = port

class Res:

    def __init__(self, type, IP, port_banner):
        self.type = type
        self.IP = IP
        self.port_banner = port_banner
