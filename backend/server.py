import uuid;
from time import sleep
from datetime import timedelta
from datetime import datetime
import requests
import threading

import jsonpickle

from config import *

import ipcalc;
from pymongo import MongoClient;
from RestAPIServer import RestAPIServer
from ReqResObjects import *

from datautil import *


LIMIT = 1000
IP_LIMIT = 100
pendingList = {}
assignedList = {}
assignedListLock = threading.Lock()

workerId = "127.0.0.1:8080"
prefixUrl = 'http://';
pendingJobCnt = 0

ip = 'localhost';
port = 27017;

# Insert a new job record in mongo database
def insertRecord(scanType, json_data):
    print "insertRecord"

    def __init__(self, ip, port):
        client = MongoClient(ip, port);
        db = client.test_database
        records = db.records
        record_id = records.insert_one(json_data).inserted_id
        print record_id


# Send/Receive requests from RstAPI Server
def sendAndReceiveObjects(url, req):
    print "sendAndReceiveObjects" + url
    r = requests.post(url, data=jsonpickle.encode(req))
    created = r.json()['work_id']
    # print "Message ID: " + str(created), r.json()
    # r = requests.get(url + "/" + str(created))
    #print "Service returned: " + str(r.json())
    #res = jsonpickle.decode(r.text)
    #sleep(3)
    return req


# Assign a job to worker
def assignWork(jobObj):
    global pendingJobCnt
    print "assignWork"
    print "assignedList: " + str(assignedList)
    print "pendingList: " + str(pendingList)
    print "pendingJobCnt: " + str(pendingJobCnt)

    with assignedListLock:
        for worker in assignedList:
            if (assignedList[worker] == None):
                assignedList[worker] = [jobObj, datetime.now()]
                # response = requests.get(url, data=job)
                print prefixUrl + worker
                sendAndReceiveObjects(prefixUrl + worker, jobObj)
                print "jobid: " + jobObj.jobId + " assigned to " + worker
                if (pendingJobCnt > 0):
                    pendingJobCnt -= 1
                    return


# Get a pending job from queue
def getPendingWork():
    print "getPendingWork"
    global pendingJobCnt
    jobObj = None
    if (pendingJobCnt <= 0):
        print "getPendingWork: no pending work"
    else:
        for req in pendingList:
            if (len(pendingList[req]) > 0):
                jobObj = pendingList[req].pop()
                if (jobObj):
                    print str(jobObj)
                    return jobObj
        return jobObj


# Register a new worker and assign him work
def registerWorker(workerIP_Port):
    print "registerWorker"
    with assignedListLock:
        assignedList[workerIP_Port] = None;
    print "new worker registered " + workerIP_Port;
    job = getPendingWork()
    if job: assignWork(job)

'''
# Receive request from UI and divide the work into jobs then assign them
def requestReceiver(scanIp, scanSequentially, portrange, scanType):
    res = portrange.split('-')
    startPort = int(res[0].strip())
    endPort = int(res[1].strip())
    print "requestReceiver"
    reqid = str(uuid.uuid1())
    pendingList[reqid] = [];
    range = endPort - startPort
    global pendingJobCnt

    if (scanType is TCP_FIN_SCAN or scanType is TCP_SYN_SCAN or scanType is CONNECT_SCAN):

        net = ipcalc.Network(scanIp)
        # netsize = net.size()-2

        if (range > LIMIT):
            for ip in net:
                stPort = startPort
                enPort = 0
                print scanType
                d = range / LIMIT
                for x in xrange(d + 1):
                    stPort = stPort
                    if (x == d):
                        enPort = endPort
                    else:
                        enPort = stPort + LIMIT
                    jobid = str(uuid.uuid1());
                    jobObj = Job(scanType, [scanIp],True, stPort, enPort, jobid, reqid)
                    print str(jobObj)
                    pendingList[reqid].append(jobObj);
                    pendingJobCnt += 1
                    stPort = enPort + 1
                    assignWork(jobObj);
                    # print "Work Pending for reqid: " + reqid +"::::"+ str(pendingList[reqid]);
        else:
            IPs = []
            stPort = startPort
            enPort = endPort
            chkCnt = 1
            cnt = 1
            for ip in net:
                print str(ip), len(IPs), net.size()
                if (net.size() > 1):
                    if ((len(IPs) + 1) * range < LIMIT and cnt < net.size() - 2):
                        IPs.append(str(ip))
                    else:
                        jobid = str(uuid.uuid1())
                        jobObj = Job(scanType, IPs, True ,stPort, enPort, jobid, reqid)
                        print str(jobObj.IPs), str(jobObj.ports)
                        pendingList[reqid].append(jobObj)
                        pendingJobCnt += 1
                        assignWork(jobObj)
                        IPs = []
                        IPs.append(str(ip))
                    cnt += 1
                else:
                    jobid = str(uuid.uuid1())
                    jobObj = Job(scanType, [scanIp], True, stPort, enPort, jobid, reqid)
                    print str(jobObj.IPs), str(jobObj.ports)
                    pendingList[reqid].append(jobObj)
                    pendingJobCnt += 1
                    assignWork(jobObj)

    elif (scanType is IS_UP_BULK):
        print "IS_UP_BULK"
        net = ipcalc.Network(scanIp)
        netsize = net.size() - 2
        d = (netsize) / IP_LIMIT
        print "size" + str(net.size()) + str(d)
        chkCnt = 1
        cnt = 1
        IPs = []
        for ip in net:
            print str(ip), str(cnt)
            IPs.append(str(ip))
            if ((IP_LIMIT * chkCnt == cnt or netsize == cnt)):
                chkCnt += 1
                jobid = str(uuid.uuid1())
                jobObj = Job(scanType, IPs, True, 1, 100,jobid, reqid)
                print str(jobObj)
                pendingList[reqid].append(jobObj)
                pendingJobCnt += 1
                assignWork(jobObj)
                IPs = []
            cnt += 1
    return json.dumps([{"reqid":reqid,"numjob":len(pendingList[reqid])}])
'''
def getWorkerCnt():
    print "getWorkerCnt"
    workerCnt = 0
    for worker in assignedList:
        workerCnt +=1
    return workerCnt


def requestReceiver(scanIp, scanSequentially, portrange, scanType):

    res = portrange.split('-')
    startPort = int(res[0].strip())
    endPort = int(res[1].strip())
    print "requestReceiver"

    global pendingJobCnt

    print "requestReceiver"
    reqid = str(uuid.uuid1())
    pendingList[reqid] = []
    workerCnt = getWorkerCnt()
    portRange = endPort - startPort + 1
    ipRange = 0
    global pendingJobCnt
    if(ipcalc.Network(scanIp).size()==1): ipRange = 1
    else:  ipRange = ipcalc.Network(scanIp).size()-2

    numItems = ipRange * portRange
    print "portRange: " + str(portRange)
    print "ipRange: " + str(ipRange)
    print "numItems: " + str(numItems)
    workDiv = numItems/workerCnt
    itemrem = numItems%workerCnt
    #cnt=1
    #ipcnt=0

    workLimit=workDiv
    if(workDiv>LIMIT):
        workLimit=LIMIT

    if (scanType is TCP_FIN_SCAN or scanType is TCP_SYN_SCAN or scanType is CONNECT_SCAN):

        if(numItems > workerCnt):
            jobItemCnt=0
            jobItem=[]
            for ip in ipcalc.Network(scanIp):
                rangeCnt=0
                while(rangeCnt<portRange):
                    if((jobItemCnt+portRange)<=workLimit and (rangeCnt+portRange)<=portRange):

                        jobItem.append([str(ip),startPort,endPort])
                        jobItemCnt=jobItemCnt+portRange
                        rangeCnt=rangeCnt+portRange
                        print "jobItem: "+ str(ip) + ":"+str(startPort)+"->"+str(endPort)
                        #elif(jobItemCnt==workLimit):
                        #make job of it directly and move to next job
                    else:
                        if((rangeCnt+(workLimit-jobItemCnt))<=portRange):
                            jobItem.append([str(ip),rangeCnt+1,rangeCnt+(workLimit-jobItemCnt)])
                            rangeCnt=rangeCnt+(workLimit-jobItemCnt)
                            jobItemCnt=jobItemCnt+(workLimit-jobItemCnt)

                            print "jobItem: "+ str(ip) + ":"+str(rangeCnt+1)+"->"+str(rangeCnt+(workLimit-jobItemCnt))
                            jobid = str(uuid.uuid1())
                            jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                            pendingList[reqid].append(jobObj)
                            pendingJobCnt += 1
                            print "jobItemCnt: " +str(jobItemCnt)
                            print "pendingList[reqid]" + str(pendingList[reqid])

                            print "jobItem"+jobItem
                            #make job with
                            jobItem=[]
                            jobItemCnt=0
                        else:
                            jobItem.append([str(ip),rangeCnt+1,rangeCnt+(portRange-rangeCnt)])
                            rangeCnt=rangeCnt+(portRange-rangeCnt)
                            jobItemCnt=jobItemCnt+(portRange-rangeCnt)
                            print "jobItem: "+ str(ip) + ":"+str(rangeCnt+1)+"->"+str(rangeCnt+(portRange-rangeCnt))
                            jobid = str(uuid.uuid1())
                            jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                            pendingList[reqid].append(jobObj)
                            pendingJobCnt += 1
                            print "jobItemCnt: " +str(jobItemCnt)
                            print "pendingList[reqid]" + str(pendingList[reqid])
                            print "jobItem"+jobItem

                        #jobItem.append([str(ip),startPort+(workLimit-jobItemCnt)+1,endPort])
                        #print "jobItem: "+ str(ip) + ":"+str(startPort)+"->"+str(endPort)
        else:
            jobItem=[]
            jobItemCnt=0
            for ip in ipcalc.Network(scanIp):
                for port in range(startPort,endPort+1):
                    jobItemCnt +=1
                    #jobItem.append([str(ip),port,port])
                    print "jobItem: "+ str(ip) + ":"+str(port)+"->"+str(port)
                    pendingList[reqid].append([str(ip),port,port])
                    pendingJobCnt += 1
                    print "pendingList[reqid]" + str(pendingList[reqid])

    elif (scanType is IS_UP_BULK):
        print "IS_UP_BULK"

        net = ipcalc.Network(scanIp)
        netsize = ipRange

        d = (netsize) / IP_LIMIT
        print "size" + str(net.size()) + str(d)
        chkCnt = 1
        cnt = 0
        IPPorts = []
        for ip in net:
            print str(ip), str(cnt)
            IPPorts.append([str(ip),None,None])
            if ((workLimit * chkCnt == cnt or netsize == cnt)):
                chkCnt += 1
                jobid = str(uuid.uuid1())
                jobObj = Job(scanType, IPPorts, scanSequentially, jobid, reqid)
                print str(jobObj)
                pendingList[reqid].append(jobObj)
                pendingJobCnt += 1
                assignWork(jobObj)
                IPPorts = []
            cnt += 1

    return json.dumps([{"reqid":reqid,"numjob":len(pendingList[reqid])}])




def processReport(reqId, jobId, scanType, report):

    print "processReport: " + report
    #insertRecord(scanType, report)

    client = setup()
    insertdata(client, report, scanType)

    # jobObj = Job(scanType ,["127.0.0.1"], 1, 100, jobId, reqId)
    for key in pendingList:
        if (key == reqId):
            # pendingList[reqId].remove(jobObj)
            if not pendingList[reqId]:
                print "reqid: " + reqId + "completed"


# Receive job report from worker
def receiveJobReport(res):
    print "receiveJobReport1: assignedList" + str(assignedList)
    print "receiveJobReport1: pendingList" + str(pendingList)

    jobId = res.jobId
    reqId = res.reqId
    workerId = res.workerIP_Port
    scanType = res.scanType
    with assignedListLock:
        if (assignedList[workerId] != None and assignedList[workerId][0].jobId == jobId):
            assignedList[workerId] = None;
            print "jobid: " + jobId + "done by workerId: " + workerId;

    processReport(reqId, jobId, scanType, jsonpickle.encode(res))
    job = getPendingWork()
    print job
    if (job):
        assignWork(job)
    else:
        print "No jobs to do"
    print "receiveJobReport2: assignedList" + str(assignedList)
    print "receiveJobReport2: pendingList" + str(pendingList)
    return


# Rest Server started
class MyRestServer(RestAPIServer):
    def doJob(self, job):
        if type(job) == HeartBeat:
            workerID = job.workerIP_Port
            if workerID not in assignedList:
                registerWorker(workerID)
            else:
                if assignedList[workerID]:
                    assignedList[workerID][1] = job.aliveAt

        elif type(job) == Res:
            receiveJobReport(job)
        print "Doing something..."

    def run_server(self):
        super(MyRestServer, self).run_server()
        threading.Thread(target=self.reaper).start()

    def reaper(self):
        global pendingJobCnt, HEARTBEATS_SKIPPED_BEFORE_REAPING, TIME_IN_SEC_BETWEEN_HEARTBEATS
        while (True):
            with assignedListLock:
                for workerID in assignedList:
                    if assignedList[workerID] and assignedList[workerID][1] > datetime.now() + timedelta(
                            seconds=HEARTBEATS_SKIPPED_BEFORE_REAPING * TIME_IN_SEC_BETWEEN_HEARTBEATS):
                        job, lastresponsetime = assignedList.pop(workerID)
                        print 'Removed unresponsive worker {0}'.format(workerID)
                        pendingList[job.reqId].append(job)
                        pendingJobCnt += 1
                        print 'Added job[{0}] back to pending list of req[{1}]'.format(jsonpickle.encode(job),
                                                                                       jsonpickle.encode(
                                                                                           pendingList[job.reqId]))
            sleep(2)


if __name__ == '__main__':
    srvr = MyRestServer()
    srvr.run_server()

    # sleep(15)
    # sendAndReceiveObjects(URL, Register("27.0.0.0.1",8080))
    # registerWorker("172.24.31.198",8080)
    #sleep(3)

    #requestReceiver("130.245.124.254", 1, 1200, TCP_FIN_SCAN);


    #requestReceiver("172.24.22.0/26", 1, 1200, TCP_FIN_SCAN);
    #requestReceiver("130.245.124.254", 1, 5000, TCP_FIN_SCAN);
    #requestReceiver("172.24.22.0/26", 1, 2000, IS_UP_BULK);

    #processReport("123", "123", "conn", {ip: "123.32.34.45" })

    #requestReceiver("130.245.124.254", 1, 11000, CONNECT_SCAN);

    #print requestReceiver("130.245.124.254", 1, 3000, TCP_FIN_SCAN);

    requestReceiver("130.245.124.254", True, "1-3200", TCP_FIN_SCAN)

    #requestReceiver("127.0.0.1", 8000, 9500, CONNECT_SCAN);

    #registerWorker("27.0.0.0.1",8080)
    #print pendingJobCnt;


