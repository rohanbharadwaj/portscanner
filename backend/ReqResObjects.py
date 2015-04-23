__author__ = 'rami'

from datetime import datetime

IS_UP_BULK = "IS_UP_BULK"
IS_UP = "IS_UP"
TCP_SYN_SCAN = "TCP_SYN_SCAN"
CONNECT_SCAN = "CONNECT_SCAN"
TCP_FIN_SCAN = "TCP_FIN_SCAN"


class HeartBeat(object):
    def __init__(self, ip, port):
        self.workerIP_Port = '{0}:{1}'.format(ip, port)
        self.aliveAt = datetime.now()


class Req(object):
    def __init__(self, scanType, IPs, ports=list(range(1, 100))):
        self.scanType = scanType
        self.IPs = IPs
        self.ports = ports


class Job(Req):
    def __init__(self, scanType, IPs, scanSequentially=True, startPort=1, endPort=100, jobId=None, reqId=None):
        self.scanSequentially = scanSequentially
        self.scanType = scanType
        self.IPs = IPs
        self.ports = list(range(startPort, endPort + 1))
        self.jobId = jobId
        self.reqId = reqId

    def __eq__(self, other):
        if (other == None):
            return False
        print self.jobId + ":::::::" + other.jobId, self.jobId == other.jobId
        return self.jobId == other.jobId

    def __cmp__(self, other):
        if (other == None):
            return False
        return cmp(self.jobId, other.jobId)


class Res(object):
    def __init__(self, job):
        self.workerIP_Port = '{0}:{1}'
        self.scanType = job.scanType
        self.IPs = job.IPs
        self.ports = job.ports
        self.jobId = job.jobId
        self.reqId = job.reqId
        self.report = None