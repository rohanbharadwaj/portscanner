import uuid;
import json;
from time import sleep
import requests

import jsonpickle

import ipcalc;
from pymongo import MongoClient;
from RestAPIServer import RestAPIServer
from ReqResObjects import *


LIMIT = 1000
IP_LIMIT = 100
pendingList = {}
assignedList = {}

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
    #print "Message ID: " + str(created), r.json()
    #r = requests.get(url + "/" + str(created))
    #print "Service returned: " + str(r.json())
    #res = jsonpickle.decode(r.text)
    #sleep(3)
    return req

# Assign a job to worker
def assignWork(jobObj):
    print "assignWork"
    print "assignedList: "+ str(assignedList)
    print "pendingList: "+ str(pendingList)
    print "pendingJobCnt: "+ str(pendingJobCnt)
    global pendingJobCnt
    for worker in assignedList:
        if(assignedList[worker]==None):
            assignedList[worker] = jobObj.jobId
            #response = requests.get(url, data=job)
            print prefixUrl+worker
            sendAndReceiveObjects(prefixUrl+worker,jobObj)
            print "jobid: " + jobObj.jobId + " assigned to " + worker
            if(pendingJobCnt>0):
                pendingJobCnt -=1
                return

# Get a pending job from queue
def getPendingWork():
    print "getPendingWork"
    global pendingJobCnt
    jobObj=None
    if(pendingJobCnt<=0):
        print "getPendingWork: no pending work"
    else:
        for req in pendingList:
            if(len(pendingList[req])>0):
                jobObj = pendingList[req].pop()
                if(jobObj):
                    print str(jobObj)
                    return jobObj
        return jobObj



# Register a new worker and assign him work
def registerWorker(ip,port):
    print "registerWorker"
    assignedList[ip+":"+str(port)] = None;
    print "new worker registered " + ip + ":" + str(port);
    job = getPendingWork()
    assignWork(job)


# Receive request from UI and divide the work into jobs then assign them
def requestReceiver(scanIp, startPort, endPort, scanType):
    print "requestReceiver"
    reqid = str(uuid.uuid1())
    pendingList[reqid] = [];
    range = endPort - startPort
    global pendingJobCnt

    if(scanType is TCP_FIN_SCAN or scanType is TCP_SYN_SCAN or scanType is CONNECT_SCAN):

        net = ipcalc.Network(scanIp)
        #netsize = net.size()-2

        if(range > LIMIT):
            for ip in net:
                stPort = startPort
                enPort = 0
                print scanType
                d = range/LIMIT
                for x in xrange(d+1):
                    stPort = stPort
                    if (x == d):
                        enPort = endPort
                    else:
                        enPort = stPort + LIMIT
                    jobid = str(uuid.uuid1());
                    jobObj = Job(scanType ,[scanIp], stPort, enPort, jobid, reqid)
                    print str(jobObj)
                    pendingList[reqid].append(jobObj);
                    pendingJobCnt += 1
                    stPort = enPort+1
                    assignWork(jobObj);
                #print "Work Pending for reqid: " + reqid +"::::"+ str(pendingList[reqid]);
        else:
            IPs = []
            stPort = startPort
            enPort = endPort
            chkCnt = 1
            cnt = 1
            for ip in net:
                print str(ip), len(IPs), net.size()
                if(net.size()>1):
                    if((len(IPs)+1)*range<LIMIT and cnt<net.size()-2):
                        IPs.append(str(ip))
                    else:
                        jobid = str(uuid.uuid1())
                        jobObj = Job(scanType ,IPs , stPort, enPort, jobid, reqid)
                        print str(jobObj.IPs),str(jobObj.ports)
                        pendingList[reqid].append(jobObj)
                        pendingJobCnt += 1
                        assignWork(jobObj)
                        IPs = []
                        IPs.append(str(ip))
                    cnt +=1
                else:
                    jobid = str(uuid.uuid1())
                    jobObj = Job(scanType ,[scanIp] , stPort, enPort, jobid, reqid)
                    print str(jobObj.IPs),str(jobObj.ports)
                    pendingList[reqid].append(jobObj)
                    pendingJobCnt += 1
                    assignWork(jobObj)

    elif(scanType is IS_UP_BULK):
        print "IS_UP_BULK"
        net = ipcalc.Network(scanIp)
        netsize = net.size()-2
        d = (netsize) / IP_LIMIT
        print "size" + str(net.size()) + str(d)
        chkCnt = 1
        cnt = 1
        IPs = []
        for ip in net:
            print str(ip), str(cnt)
            IPs.append(str(ip))
            if((IP_LIMIT*chkCnt==cnt or netsize==cnt)):
                chkCnt +=1
                jobid = str(uuid.uuid1())
                jobObj = Job(scanType ,IPs , 0, 100, jobid, reqid)
                print str(jobObj)
                pendingList[reqid].append(jobObj)
                pendingJobCnt += 1
                assignWork(jobObj)
                IPs = []
            cnt +=1


def processReport(reqId, jobId, scanType, report):
    print "processReport: " + report
    insertRecord(scanType, report)
    #jobObj = Job(scanType ,["127.0.0.1"], 1, 100, jobId, reqId)
    for key in pendingList:
        if(key == reqId):
            #pendingList[reqId].remove(jobObj)
            if not pendingList[reqId]:
                print "reqid: "+ reqId + "completed"


# Receive job report from worker
def receiveJobReport(res):
    print "receiveJobReport1: assignedList" + str(assignedList)
    print "receiveJobReport1: pendingList" + str(pendingList)

    jobId = res.jobId
    reqId = res.reqId
    workerId = res.workerIP_Port
    scanType = res.scanType
    if(assignedList[workerId]!=None and assignedList[workerId]==jobId):
        assignedList[workerId]= None;
        print "jobid: "+ jobId +"done by workerId: "+workerId;

    processReport(reqId, jobId, scanType, jsonpickle.encode(res))
    job = getPendingWork()
    print job
    if(job):
        assignWork(job)
    else:
        print "No jobs to do"
    print "receiveJobReport2: assignedList" + str(assignedList)
    print "receiveJobReport2: pendingList" + str(pendingList)
    return

# Rest Server started
class MyRestServer(RestAPIServer):
    def doJob(self, job):
        if type(job) == Register:
            registerWorker(job.IP,job.port)
        elif type(job) == Res:
            receiveJobReport(job)
        print "Doing something..."



if __name__ == '__main__':
    srvr = MyRestServer()
    srvr.run_server()

    # sleep(15)
    #sendAndReceiveObjects(URL, Register("27.0.0.0.1",8080))
    #registerWorker("172.24.31.198",8080)
    #sleep(3)

    #requestReceiver("130.245.124.254", 1, 1200, TCP_FIN_SCAN);
    #requestReceiver("172.24.22.0/24", 1, 1200, TCP_FIN_SCAN);
    requestReceiver("130.245.124.254", 1, 200, TCP_FIN_SCAN);

    #requestReceiver("127.0.0.1", 8000, 9500, CONNECT_SCAN);

    #registerWorker("27.0.0.0.1",8080)
    #print pendingJobCnt;


'''
def createJob(jobid, reqid, scanIp, startPort, endPort, scanType):
    data = {}
    json_data =  json.dumps({})
    data['jobid'] = jobid
    data['reqid'] = reqid
    data['scanIp'] = scanIp
    data['startPort'] = startPort
    data['endPort'] = endPort
    data['scanType'] = scanType
    json_data = json.dumps(data)
    return json_data
'''