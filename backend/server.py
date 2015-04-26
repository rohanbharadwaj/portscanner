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

from dataBack import *


LIMIT = 2**30
CONN_LIMIT = 1000
pendingList = {}
assignedList = {}
assignedListLock = threading.Lock()

workerId = "127.0.0.1:8080"
prefixUrl = 'http://';

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

def getPendingJobCnt():
    pendingJobCnt =0
    for req in pendingList:
        pendingJobCnt= pendingJobCnt+ len(pendingList[req])
    return pendingJobCnt

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
def assignWork():
    print "assignWork"
    print "assignedList: " + str(assignedList)
    print "pendingList: " + str(pendingList)
    print "pendingJobCnt: " + str(getPendingJobCnt())

    with assignedListLock:
        for worker in assignedList:
            if (assignedList[worker] == None):
                jobObj = getPendingWork()
                if(jobObj):
                    assignedList[worker] = [jobObj, datetime.now()]
                    # response = requests.get(url, data=job)
                    print prefixUrl + worker
                    sendAndReceiveObjects(prefixUrl + worker, jobObj)
                    print "jobid: " + jobObj.jobId + " assigned to " + worker
                else:
                    print "assignWork: no pending work"
                #if (pendingJobCnt > 0):
                #    pendingJobCnt -= 1
                #    return


# Get a pending job from queue
def getPendingWork():
    print "getPendingWork"
    #global pendingJobCnt
    jobObj = None
    if (getPendingJobCnt() <= 0):
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
    assignWork()


def getWorkerCnt():
    print "getWorkerCnt"
    workerCnt = 0
    for worker in assignedList:
        workerCnt +=1
    return workerCnt


def requestReceiver(scanIp, scanSequentially, portrange, scanType):
    print "requestReceiver ", scanType
    res = portrange.split('-')
    startPort = int(res[0].strip())
    endPort = int(res[1].strip())

    reqid = str(uuid.uuid1())
    pendingList[reqid] = []
    workerCnt = 5 #getWorkerCnt()
    portRange = endPort - startPort + 1
    ipRange = 0

    if(scanType==IS_UP_BULK):
       portRange=1

    if(ipcalc.Network(scanIp).size()==1): ipRange = 1
    else:  ipRange = ipcalc.Network(scanIp).size()-2

    numItems = ipRange * portRange

    print "workerCnt: " + str(workerCnt)
    print "portRange: " + str(portRange)
    print "ipRange: " + str(ipRange)
    print "numItems: " + str(numItems)
    workDiv = 0
    workLimit = 0
    itemrem=0

    if(workerCnt==0):
        workLimit = LIMIT
    else:
        workDiv = numItems/workerCnt
        itemrem = numItems%workerCnt
        workLimit=workDiv
        if(workDiv>LIMIT):
             workLimit=LIMIT
        if(scanType==CONNECT_SCAN):
            workLimit=CONN_LIMIT

    print "workLimit: " + str(workLimit)
    print "itemrem: " + str(itemrem)

    if (scanType==TCP_FIN_SCAN or scanType==TCP_SYN_SCAN or scanType==CONNECT_SCAN):

        if(numItems > workerCnt):
            itemCnt = 0 #count of total items
            jobItemCnt=0
            jobItem=[]
            for ip in ipcalc.Network(scanIp):
                rangeCnt=0
                while(rangeCnt<portRange):
                    if((jobItemCnt+portRange)<=workLimit and (rangeCnt+portRange)<=portRange):

                        jobItem.append([str(ip),startPort,endPort])
                        itemCnt = itemCnt + portRange
                        jobItemCnt=jobItemCnt+portRange
                        rangeCnt=rangeCnt+portRange
                        #print "jobItem: "+ str(ip) + ":"+str(startPort)+"->"+str(endPort)
                        print "jobItem"+str(jobItem)
                        #elif(jobItemCnt==workLimit):
                        #make job of it directly and move to next job
                    else:
                        if((rangeCnt+(workLimit-jobItemCnt))<=portRange):
                            jobItem.append([str(ip),startPort+rangeCnt,startPort+rangeCnt+(workLimit-jobItemCnt)])
                            itemCnt = itemCnt + (workLimit-jobItemCnt)
                            rangeCnt=rangeCnt+(workLimit-jobItemCnt)
                            jobItemCnt=jobItemCnt+(workLimit-jobItemCnt)

                            #print "jobItem: "+ str(ip) + ":"+str(rangeCnt+1)+"->"+str(rangeCnt+(workLimit-jobItemCnt))
                            #jobid = str(uuid.uuid1())


                            #jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                            #pendingList[reqid].append(jobObj)

                            #pendingJobCnt += 1
                            #job = getPendingWork()
                            #if(job): assignWork(job);

                            #print "jobItemCnt: " +str(jobItemCnt)
                            print "jobItem"+str(jobItem)
                            print "pendingList[reqid]" + str(pendingList[reqid])

                            #make job with
                            #jobItem=[]
                            #jobItemCnt=0
                        else:
                            jobItem.append([str(ip),startPort+rangeCnt,startPort+rangeCnt+(portRange-1-rangeCnt)])
                            itemCnt = itemCnt + (portRange-rangeCnt)
                            rangeCnt=rangeCnt+(portRange-rangeCnt)
                            jobItemCnt=jobItemCnt+(portRange-rangeCnt)
                            #print "jobItem: "+ str(ip) + ":"+str(rangeCnt+1)+"->"+str(rangeCnt+(portRange-rangeCnt))
                            #jobid = str(uuid.uuid1())
                            #jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                            #pendingList[reqid].append(jobObj)
                            #pendingJobCnt += 1
                            #job = getPendingWork()
                            #if(job): assignWork(job);

                            #print "jobItemCnt: " +str(jobItemCnt)
                            print "jobItem"+str(jobItem)
                            print "pendingList[reqid]" + str(pendingList[reqid])

                    if(jobItemCnt==workLimit or itemCnt==numItems):
                        print "jobItemCnt==workLimit111111111"
                        jobid = str(uuid.uuid1())
                        jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                        pendingList[reqid].append(jobObj)
                        jobItem=[]
                        jobItemCnt=0
                    elif(jobItemCnt>workLimit):
                        print "error:::::::::::jobItemCnt>workLimit"
                # if(jobItemCnt==workLimit or itemCnt==numItems):
                #     print "jobItemCnt==workLimit2222222222222"
                #     jobid = str(uuid.uuid1())
                #     jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                #     pendingList[reqid].append(jobObj)
                #     jobItem=[]
                #     jobItemCnt=0
                # elif(jobItemCnt>workLimit):
                #     print "error:::::::::::jobItemCnt>workLimit"
                #         #jobItem.append([str(ip),startPort+(workLimit-jobItemCnt)+1,endPort])
                #         #print "jobItem: "+ str(ip) + ":"+str(startPort)+"->"+str(endPort)
        else:
            jobItem=[]
            jobItemCnt=0
            for ip in ipcalc.Network(scanIp):
                for port in range(startPort,endPort+1):
                    jobItemCnt +=1
                    #jobItem.append([str(ip),port,port])
                    #print "jobItem: "+ str(ip) + ":"+str(port)+"->"+str(port)
                    jobid = str(uuid.uuid1())
                    jobObj = Job(scanType, jobItem, scanSequentially, jobid, reqid)
                    pendingList[reqid].append(jobObj)
                    #pendingJobCnt += 1
                    #job = getPendingWork()
                    #if(job): assignWork(job);

                    print "jobItem"+str(jobItem)
                    print "pendingList[reqid]" + str(pendingList[reqid])

    elif (scanType ==IS_UP_BULK):
        print "IS_UP_BULK"

        net = ipcalc.Network(scanIp)
        netsize = ipRange

        d = (netsize) / workLimit
        print "size" + str(net.size()) + str(d)
        chkCnt = 1
        cnt = 0
        IPPorts = []
        for ip in net:
            print str(ip), str(cnt)
            cnt += 1
            IPPorts.append([str(ip),None,None])
            if ((workLimit * chkCnt == cnt or netsize == cnt)):
                chkCnt += 1
                jobid = str(uuid.uuid1())
                jobObj = Job(scanType, IPPorts, scanSequentially, jobid, reqid)
                print str(jobObj)
                pendingList[reqid].append(jobObj)
                #pendingJobCnt += 1
                IPPorts = []
            #cnt += 1

    response = json.dumps([{"reqid":reqid,"numjob":len(pendingList[reqid])}])
    for jobitem in pendingList[reqid]:
        assignWork()
    print response
    return response

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
    assignWork()
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
        global  HEARTBEATS_SKIPPED_BEFORE_REAPING, TIME_IN_SEC_BETWEEN_HEARTBEATS
        while (True):
            with assignedListLock:
                for workerID in assignedList:
                    if assignedList[workerID] and assignedList[workerID][1] > datetime.now() + timedelta(
                            seconds=HEARTBEATS_SKIPPED_BEFORE_REAPING * TIME_IN_SEC_BETWEEN_HEARTBEATS):
                        job, lastresponsetime = assignedList.pop(workerID)
                        print 'Removed unresponsive worker {0}'.format(workerID)
                        pendingList[job.reqId].append(job)
                        #pendingJobCnt += 1
                        print 'Added job[{0}] back to pending list of req[{1}]'.format(jsonpickle.encode(job),
                                                                                       jsonpickle.encode(
                                                                                           pendingList[job.reqId]))
            sleep(2)


if __name__ == '__main__':
    #srvr = MyRestServer()
    #srvr.run_server()

    # sleep(15)
    # sendAndReceiveObjects(URL, Register("27.0.0.0.1",8080))
    # registerWorker("172.24.31.198",8080)
    #sleep(3)

    #requestReceiver("130.245.124.254", 1, 1200, TCP_FIN_SCAN);


    #requestReceiver("172.24.22.0/26", 1, 1200, TCP_FIN_SCAN);
    #requestReceiver("130.245.124.254", 1, 5000, TCP_FIN_SCAN);
    requestReceiver("172.24.2.20/24", True, "20-31", TCP_FIN_SCAN);

    #processReport("123", "123", "conn", {ip: "123.32.34.45" })

    #requestReceiver("130.245.124.254", 1, 1000, CONNECT_SCAN);

    #print requestReceiver("130.245.124.254", 1, 3000, TCP_FIN_SCAN);


    #requestReceiver("172.16.42.0/30", True, "1-100", TCP_FIN_SCAN)

    #requestReceiver("130.245.124.254/26", True, "1-100", TCP_FIN_SCAN)

    #requestReceiver("127.0.0.1", 8000, 9500, CONNECT_SCAN);

    #registerWorker("27.0.0.0.1",8080)
    #print pendingJobCnt;
