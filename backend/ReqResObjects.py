__author__ = 'rami'

IS_UP_BULK = "IS_UP_BULK"
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"


class Req(object):
    def __init__(self, type, IPs, ports=list(range(1, 100))):
        self.type = type
        self.IPs = IPs
        self.ports = ports


class Job(Req):
    def __init__(self, scanType, IPs, startPort=1, endPort=1, jobId=None, reqId=None):
        # super(Job, self).__init__(scanType, IPs, ports)
        self.type = type
        self.IPs = IPs
        self.ports = list(range(startPort, endPort + 1))
        self.jobId = jobId
        self.reqId = reqId


class Register(object):
    def __init__(self, IP, port):
        self.IP = IP
        self.port = port


class Res(object):
    def __init__(self, job):
        self.type = job.type
        self.IPs = job.IPs
        self.ports = job.ports
        self.jobId = job.jobId
        self.reqId = job.reqId
        self.report = None