__author__ = 'rami'

IS_UP_BULK = "IS_UP_BULK"
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"


class Req(object):
    def __init__(self, scanType, IPs, ports=list(range(1, 100))):
        self.scanType = scanType
        self.IPs = IPs
        self.ports = ports


class Job(Req):
    def __init__(self, scanType, IPs, startPort=1, endPort=100, jobId=None, reqId=None):
        # super(Job, self).__init__(scanType, IPs, ports)
        self.scanType = scanType
        self.IPs = IPs
        self.ports = list(range(startPort, endPort + 1))
        self.jobId = jobId
        self.reqId = reqId
    def __eq__(self, other):
        if(other==None):
            return False
        print self.jobId+":::::::"+ other.jobId, self.jobId == other.jobId
        return self.jobId == other.jobId

    def __cmp__(self, other):
        if(other==None):
            return False
        print self.jobId+"%%%%:::"+ other.jobId, cmp(self.jobId,other.jobId)
        return cmp(self.jobId,other.jobId)


class Register(object):
    def __init__(self, IP, port):
        self.IP = IP
        self.port = port


class Res(object):
    def __init__(self, job):
        self.workerIP_Port = '{0}:{1}'
        self.scanType = job.scanType
        self.IPs = job.IPs
        self.ports = job.ports
        self.jobId = job.jobId
        self.reqId = job.reqId
        self.report = None